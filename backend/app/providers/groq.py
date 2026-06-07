"""Groq provider using OpenAI-compatible API."""

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


class GroqProvider(OpenAICompatibleProvider):
    """Groq provider with OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        super().__init__(api_key, model, "https://api.groq.com/openai/v1")

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion using Groq API with custom error handling."""
        try:
            async for token in super().chat(request):
                yield token
        except Exception as e:
            error_str = str(e).lower()
            if "authentication" in error_str or "invalid api key" in error_str:
                logger.error(f"Groq authentication error: {e}")
                raise AuthenticationError("Неверный API ключ Groq. Проверьте настройки.")
            elif "rate limit" in error_str or "429" in error_str:
                logger.error(f"Groq rate limit error: {e}")
                raise RateLimitError("Превышен лимит запросов Groq. Попробуйте позже.")
            elif "not found" in error_str or "404" in error_str:
                logger.error(f"Groq model not found: {e}")
                raise ModelNotFoundError(f"Модель {self.model} не найдена. Обновите список моделей.")
            elif "timeout" in error_str or "connection" in error_str:
                logger.error(f"Groq network error: {e}")
                raise NetworkError("Ошибка сети при подключении к Groq.")
            else:
                logger.error(f"Groq unexpected error: {e}")
                raise ProviderError(f"Ошибка провайдера Groq: {str(e)}")

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=False,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=[],
            max_context_tokens=131072,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=False,
            has_models_list=True,
            free_tier_available=True,
        )

    def _is_free_tier(self, model) -> bool:
        """Groq has free tier for all models."""
        return True
