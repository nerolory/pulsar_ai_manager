"""Local LLM provider for running models on the user's machine.

Uses llama-cpp-python for embedded GGUF inference — no Ollama required.
"""

from typing import AsyncIterator, List, Optional

from loguru import logger

from app.providers.base import BaseLLMProvider
from app.providers.factory import ProviderFactory
from app.schemas import ChatRequest, ProviderCapabilities, ModelInfo
from app.system_check import get_system_specs, check_hardware_tier
from app.configs.local_models import (
    get_model_info,
    get_all_models,
    get_recommended_model,
    can_run_model,
)
from app.model_downloader import is_model_downloaded, download_model
from app.local_inference import stream_local_chat
from app.exceptions import InvalidRequestError, ProviderError


@ProviderFactory.register(name="local_llm", default_model="phi-3-mini-3.8b", requires_api_key=False)
class LocalLLMProvider(BaseLLMProvider):
    """Provider for running local LLM models on the user's machine."""

    def __init__(self, model: str = "phi-3-mini-3.8b", **kwargs):
        self.model = model
        self._provider_name = "local_llm"
        self._specs = None
        self._tier = None
        self._can_run = False
        self._check_system_requirements()

    def _check_system_requirements(self) -> None:
        self._specs = get_system_specs()
        self._tier = check_hardware_tier(self._specs)

        model_info = get_model_info(self.model)
        if not model_info:
            logger.error(f"Model {self.model} not found in configuration")
            self._can_run = False
            return

        can_run, reason, _, _ = can_run_model(
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
        if not self._can_run:
            raise InvalidRequestError(f"local_llm_requirements:{self.model}")

        if not is_model_downloaded(self.model):
            raise InvalidRequestError(f"local_llm_not_downloaded:{self.model}")

        try:
            gpu_available = bool(self._specs and self._specs["gpu_available"])
            async for token in stream_local_chat(self.model, request, gpu_available=gpu_available):
                yield token
        except InvalidRequestError:
            raise
        except Exception as e:
            logger.error(f"Local LLM inference error: {e}")
            raise ProviderError(f"local_llm_inference:{e}") from e

    async def health_check(self) -> bool:
        if not self._can_run:
            return False
        return is_model_downloaded(self.model)

    def get_capabilities(self) -> ProviderCapabilities:
        model_info = get_model_info(self.model)
        context = model_info["context_length"] if model_info else 4096
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=False,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=[],
            max_context_tokens=context,
            streaming=True,
            pricing_model="per_request",
            has_balance_api=False,
            has_models_list=True,
            free_tier_available=True,
        )

    async def list_models(self) -> List[ModelInfo]:
        models = []
        for model_id, model_info in get_all_models().items():
            if not is_model_downloaded(model_id):
                continue

            can_run, _, _, _ = (
                can_run_model(
                    model_id,
                    self._specs["total_ram_gb"],
                    self._specs["cpu_cores"],
                    self._specs["gpu_available"],
                    self._specs["gpu_vram_gb"] if self._specs and self._specs["gpu_vram_gb"] else 0,
                )
                if self._specs
                else (False, "System not checked", None, None)
            )

            models.append(
                ModelInfo(
                    id=model_id,
                    name=model_info["name"],
                    context_length=model_info["context_length"],
                    pricing=None,
                    free_tier=True,
                    is_free=True,
                    downloaded=True,
                    can_run=can_run,
                )
            )
        return models

    async def check_balance(self) -> Optional[dict]:
        return None

    async def download_model(self, model_id: str, progress_callback=None) -> bool:
        if self._specs:
            can_run, reason, _, _ = can_run_model(
                model_id,
                self._specs["total_ram_gb"],
                self._specs["cpu_cores"],
                self._specs["gpu_available"],
                self._specs["gpu_vram_gb"] if self._specs["gpu_vram_gb"] else 0,
            )
            if not can_run:
                logger.error(f"Cannot download model {model_id}: {reason}")
                return False

        success, _message = await download_model(model_id, progress_callback)
        return success

    def get_recommended_model(self) -> Optional[str]:
        if not self._specs:
            return None
        return get_recommended_model(
            self._specs["total_ram_gb"], self._specs["cpu_cores"], self._specs["gpu_available"]
        )
