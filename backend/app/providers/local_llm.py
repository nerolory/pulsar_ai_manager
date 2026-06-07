"""Local LLM provider for running models on the user's machine.

This provider handles local LLM models with hardware requirements checking,
model downloading, and communication with the local inference engine.
"""

from typing import AsyncIterator, List, Optional

from loguru import logger

from app.providers.base import BaseLLMProvider
from app.providers.factory import ProviderFactory
from app.schemas import ChatRequest, ProviderCapabilities, ModelInfo
from app.system_check import get_system_specs, check_hardware_tier, can_run_model
from app.configs.local_models import (
    get_model_info,
    get_all_models,
    get_recommended_model,
    LOCAL_MODELS,
)
from app.model_downloader import is_model_downloaded, download_model


@ProviderFactory.register(name="local_llm", default_model="phi-3-mini-3.8b", requires_api_key=False)
class LocalLLMProvider(BaseLLMProvider):
    """Provider for running local LLM models on the user's machine."""

    def __init__(self, model: str = "phi-3-mini-3.8b", **kwargs):
        """Initialize local LLM provider.

        Args:
            model: Model identifier to use
        """
        self.model = model
        self._provider_name = "local_llm"
        self._specs = None
        self._tier = None
        self._can_run = False

        # Check system requirements on initialization
        self._check_system_requirements()

    def _check_system_requirements(self) -> None:
        """Check if system meets requirements for the selected model."""
        self._specs = get_system_specs()
        self._tier = check_hardware_tier(self._specs)

        model_info = get_model_info(self.model)
        if not model_info:
            logger.error(f"Model {self.model} not found in configuration")
            self._can_run = False
            return

        # Check if system can run this specific model
        can_run, reason = can_run_model(
            self.model,
            self._specs["total_ram_gb"],
            self._specs["cpu_cores"],
            self._specs["gpu_available"],
            self._specs["gpu_vram_gb"] if self._specs["gpu_vram_gb"] else 0,
        )

        self._can_run = can_run

        if not can_run:
            logger.warning(f"System cannot run model {self.model}: {reason}")
        else:
            logger.info(f"System can run model {self.model}")

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion from local LLM.

        Args:
            request: Chat request with messages and parameters

        Yields:
            Response tokens
        """
        if not self._can_run:
            error_msg = f"System does not meet requirements for model {self.model}"
            logger.error(error_msg)
            yield f"Error: {error_msg}"
            return

        # Check if model is downloaded
        if not is_model_downloaded(self.model):
            error_msg = f"Model {self.model} is not downloaded. Please download it first."
            logger.error(error_msg)
            yield f"Error: {error_msg}"
            return

        # TODO: Implement actual local LLM inference
        # For now, return a placeholder response
        logger.warning("Local LLM inference not yet implemented")
        yield "Local LLM inference is not yet implemented. This is a placeholder response."

    async def health_check(self) -> bool:
        """Check if local LLM is available and ready.

        Returns:
            True if system meets requirements and model is downloaded
        """
        if not self._can_run:
            return False

        if not is_model_downloaded(self.model):
            return False

        # TODO: Check if local inference engine is running
        return True

    def get_capabilities(self) -> ProviderCapabilities:
        """Return provider capabilities.

        Returns:
            ProviderCapabilities object
        """
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=False,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=[],
            max_context_tokens=4096,  # Will be updated based on model
            streaming=True,
            pricing_model="free",
            has_balance_api=False,
            has_models_list=True,
            free_tier_available=True,
        )

    async def list_models(self) -> List[ModelInfo]:
        """Return list of available local models.

        Returns:
            List of ModelInfo objects (only downloaded models)
        """
        models = []

        for model_id, model_info in get_all_models().items():
            # Only show downloaded models
            downloaded = is_model_downloaded(model_id)
            if not downloaded:
                continue

            # Check if system can run this model
            can_run, _ = (
                can_run_model(
                    model_id,
                    self._specs["total_ram_gb"] if self._specs else 0,
                    self._specs["cpu_cores"] if self._specs else 0,
                    self._specs["gpu_available"] if self._specs else False,
                    self._specs["gpu_vram_gb"] if self._specs and self._specs["gpu_vram_gb"] else 0,
                )
                if self._specs
                else (False, "System not checked")
            )

            models.append(
                ModelInfo(
                    id=model_id,
                    name=model_info["name"],
                    context_length=model_info["context_length"],
                    pricing=None,
                    free_tier=True,
                    daily_limit=None,
                    limit_tokens=None,
                    balance=None,
                    is_free=True,
                    requires_payment=False,
                    downloaded=downloaded,
                    can_run=can_run,
                )
            )

        return models

    async def check_balance(self) -> Optional[dict]:
        """Local LLM has no balance - always free.

        Returns:
            None (balance not applicable)
        """
        return None

    async def download_model(self, model_id: str, progress_callback=None) -> bool:
        """Download a model.

        Args:
            model_id: Model identifier
            progress_callback: Optional callback for progress updates

        Returns:
            True if download succeeded
        """
        # Check if system can run this model
        if self._specs:
            can_run, reason = can_run_model(
                model_id,
                self._specs["total_ram_gb"],
                self._specs["cpu_cores"],
                self._specs["gpu_available"],
                self._specs["gpu_vram_gb"] if self._specs["gpu_vram_gb"] else 0,
            )

            if not can_run:
                logger.error(f"Cannot download model {model_id}: {reason}")
                return False

        return await download_model(model_id, progress_callback)

    def get_recommended_model(self) -> Optional[str]:
        """Get recommended model based on system specs.

        Returns:
            Model ID of recommended model, or None
        """
        if not self._specs:
            return None

        return get_recommended_model(
            self._specs["total_ram_gb"], self._specs["cpu_cores"], self._specs["gpu_available"]
        )
