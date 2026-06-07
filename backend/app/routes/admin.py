from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger
from app.database import get_current_schema_version, run_pending_migrations, upgrade_schema
from app.system_check import get_system_specs, check_hardware_tier, check_cpu_features
from app.model_downloader import (
    is_model_downloaded,
    download_model,
    delete_model,
    get_downloaded_models,
    get_storage_info,
)
from app.configs.local_models import get_model_info, get_all_models, can_run_model

router = APIRouter(prefix="/admin", tags=["admin"])


class SchemaVersionResponse(BaseModel):
    version: int
    message: str


class MigrationResponse(BaseModel):
    success: bool
    message: str
    version: int | None = None


@router.get("/schema-version", response_model=SchemaVersionResponse)
async def get_schema_version():
    """Get current database schema version"""
    try:
        version = await get_current_schema_version()
        return SchemaVersionResponse(version=version, message=f"Current schema version: {version}")
    except Exception as e:
        logger.error(f"Failed to get schema version: {e}")
        raise HTTPException(status_code=500, detail="Failed to get schema version")


@router.post("/migrate", response_model=MigrationResponse)
async def run_migrations():
    """Manually run pending migrations"""
    try:
        old_version = await get_current_schema_version()
        await run_pending_migrations()
        new_version = await get_current_schema_version()

        if new_version == old_version:
            return MigrationResponse(
                success=True, message="No pending migrations to apply", version=new_version
            )

        return MigrationResponse(
            success=True,
            message=f"Migrated from version {old_version} to {new_version}",
            version=new_version,
        )
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.post("/upgrade", response_model=MigrationResponse)
async def upgrade(from_version: int, to_version: int):
    """Upgrade schema from one version to another"""
    try:
        await upgrade_schema(from_version, to_version)
        new_version = await get_current_schema_version()
        return MigrationResponse(
            success=True,
            message=f"Upgraded from version {from_version} to {new_version}",
            version=new_version,
        )
    except Exception as e:
        logger.error(f"Upgrade failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upgrade failed: {str(e)}")


class SystemSpecsResponse(BaseModel):
    """System specifications response."""

    total_ram_gb: float
    available_ram_gb: float
    cpu_cores: int
    cpu_threads: int
    cpu_freq_ghz: float
    gpu_available: bool
    gpu_name: str | None
    gpu_vram_gb: float | None
    disk_free_gb: float
    os_name: str
    os_version: str
    architecture: str


class HardwareTierResponse(BaseModel):
    """Hardware tier response."""

    tier: str
    can_run_local_llm: bool
    recommended_model: str | None
    reason: str


class SystemCheckResponse(BaseModel):
    """Complete system check response."""

    specs: SystemSpecsResponse
    tier: HardwareTierResponse
    cpu_features: dict[str, bool]


@router.get("/system-check", response_model=SystemCheckResponse)
async def check_system():
    """Check system specifications and hardware tier for local LLM support"""
    try:
        specs = get_system_specs()
        tier = check_hardware_tier(specs)
        cpu_features = check_cpu_features()

        return SystemCheckResponse(
            specs=SystemSpecsResponse(**specs),
            tier=HardwareTierResponse(**tier),
            cpu_features=cpu_features,
        )
    except Exception as e:
        logger.error(f"System check failed: {e}")
        raise HTTPException(status_code=500, detail=f"System check failed: {str(e)}")


class LocalLLMSettingsResponse(BaseModel):
    """Local LLM settings response."""

    enabled: bool
    model: str
    can_run: bool
    tier: str | None
    message: str


@router.get("/local-llm/settings", response_model=LocalLLMSettingsResponse)
async def get_local_llm_settings():
    """Get local LLM settings and check if system can run it"""
    from app.configs import settings

    try:
        specs = get_system_specs()
        tier = check_hardware_tier(specs)

        if not settings.local_llm_enabled:
            return LocalLLMSettingsResponse(
                enabled=False,
                model=settings.local_llm_model,
                can_run=tier["can_run_local_llm"],
                tier=tier["tier"],
                message="Local LLM is disabled in settings",
            )

        if not tier["can_run_local_llm"]:
            return LocalLLMSettingsResponse(
                enabled=True,
                model=settings.local_llm_model,
                can_run=False,
                tier=tier["tier"],
                message=f"System does not meet requirements: {tier['reason']}",
            )

        return LocalLLMSettingsResponse(
            enabled=True,
            model=settings.local_llm_model,
            can_run=True,
            tier=tier["tier"],
            message=f"System can run local LLM. Recommended: {tier['recommended_model']}",
        )
    except Exception as e:
        logger.error(f"Failed to get local LLM settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get local LLM settings: {str(e)}")


class ModelListResponse(BaseModel):
    """List of available local models."""

    models: dict[str, dict]
    downloaded: list[str]
    storage_info: dict


@router.get("/local-llm/models", response_model=ModelListResponse)
async def list_local_models():
    """Get list of available local models and their status"""
    try:
        all_models = get_all_models()
        downloaded = get_downloaded_models()
        storage_info = get_storage_info()

        # Add download status and can_run status to each model
        models_with_status = {}
        for model_id, model_info in all_models.items():
            models_with_status[model_id] = {**model_info, "downloaded": model_id in downloaded}

        return ModelListResponse(
            models=models_with_status, downloaded=downloaded, storage_info=storage_info
        )
    except Exception as e:
        logger.error(f"Failed to list local models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list local models: {str(e)}")


class DownloadModelResponse(BaseModel):
    """Response for model download request."""

    success: bool
    message: str


@router.post("/local-llm/download/{model_id}", response_model=DownloadModelResponse)
async def download_local_model(model_id: str):
    """Download a local LLM model"""
    try:
        # Check if model exists
        model_info = get_model_info(model_id)
        if not model_info:
            return DownloadModelResponse(success=False, message=f"Model {model_id} not found")

        # Check if system can run this model
        specs = get_system_specs()
        can_run, reason = can_run_model(
            model_id,
            specs["total_ram_gb"],
            specs["cpu_cores"],
            specs["gpu_available"],
            specs["gpu_vram_gb"] if specs["gpu_vram_gb"] else 0,
        )

        if not can_run:
            return DownloadModelResponse(
                success=False, message=f"System cannot run this model: {reason}"
            )

        # Download model
        success = await download_model(model_id)

        if success:
            return DownloadModelResponse(
                success=True, message=f"Model {model_id} downloaded successfully"
            )
        else:
            return DownloadModelResponse(
                success=False, message=f"Failed to download model {model_id}"
            )
    except Exception as e:
        logger.error(f"Failed to download model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download model: {str(e)}")


class DeleteModelResponse(BaseModel):
    """Response for model delete request."""

    success: bool
    message: str


@router.delete("/local-llm/delete/{model_id}", response_model=DeleteModelResponse)
async def delete_local_model(model_id: str):
    """Delete a downloaded local LLM model"""
    try:
        success = delete_model(model_id)

        if success:
            return DeleteModelResponse(
                success=True, message=f"Model {model_id} deleted successfully"
            )
        else:
            return DeleteModelResponse(
                success=False, message=f"Failed to delete model {model_id} or model not found"
            )
    except Exception as e:
        logger.error(f"Failed to delete model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")
