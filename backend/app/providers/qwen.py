"""Qwen provider using OpenAI-compatible API (Alibaba Cloud)."""

from typing import AsyncIterator
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.schemas import ChatRequest, ProviderCapabilities
from app.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError,
    ProviderError,
)
from loguru import logger


class QwenProvider(OpenAICompatibleProvider):
    """Qwen provider with OpenAI-compatible API (Alibaba Cloud)."""

    def __init__(self, api_key: str, model: str = "qwen-max"):
        super().__init__(api_key, model, "https://dashscope.aliyuncs.com/compatible-mode/v1")

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion using Qwen API with custom error handling."""
        try:
            async for token in super().chat(request):
                yield token
        except Exception as e:
            error_str = str(e).lower()
            if "authentication" in error_str or "invalid api key" in error_str:
                logger.error(f"Qwen authentication error: {e}")
                raise AuthenticationError("Неверный API ключ Qwen. Проверьте настройки.")
            elif "rate limit" in error_str or "429" in error_str:
                logger.error(f"Qwen rate limit error: {e}")
                raise RateLimitError("Превышен лимит запросов Qwen. Попробуйте позже.")
            elif "not found" in error_str or "404" in error_str:
                logger.error(f"Qwen model not found: {e}")
                raise ModelNotFoundError(f"Модель {self.model} не найдена. Обновите список моделей.")
            elif "timeout" in error_str or "connection" in error_str:
                logger.error(f"Qwen network error: {e}")
                raise NetworkError("Ошибка сети при подключении к Qwen.")
            else:
                logger.error(f"Qwen unexpected error: {e}")
                raise ProviderError(f"Ошибка провайдера Qwen: {str(e)}")

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=True,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=["jpg", "jpeg", "png", "gif", "webp"],
            max_context_tokens=32000,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=True,
            has_models_list=True,
            free_tier_available=True,
        )

    def _is_free_tier(self, model) -> bool:
        """Qwen has free tier for all models."""
        return True
