from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger
from app.database import get_current_schema_version, run_pending_migrations, upgrade_schema

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
        return SchemaVersionResponse(
            version=version,
            message=f"Current schema version: {version}"
        )
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
                success=True,
                message="No pending migrations to apply",
                version=new_version
            )
        
        return MigrationResponse(
            success=True,
            message=f"Migrated from version {old_version} to {new_version}",
            version=new_version
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
            version=new_version
        )
    except Exception as e:
        logger.error(f"Upgrade failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upgrade failed: {str(e)}")
