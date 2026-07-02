"""Mistral AI provider using native SDK."""

import asyncio
from typing import AsyncIterator, List

from loguru import logger
from mistralai import Mistral

from app.providers.base import BaseLLMProvider
from app.providers.factory import ProviderFactory
from app.providers.media_utils import to_mistral_content
from app.schemas import ChatRequest, ProviderCapabilities, ModelInfo
from app.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError,
    ProviderError,
)


def _map_mistral_error(error: Exception, model: str) -> ProviderError:
    """Map a Mistral SDK exception to a typed ProviderError.

    Args:
        error: The original exception.
        model: Current model name for error messages.

    Returns:
        Typed ProviderError subclass.
    """
    error_str = str(error).lower()
    if "authentication" in error_str or "invalid api key" in error_str:
        logger.error(f"Mistral authentication error: {error}")
        return AuthenticationError("Неверный API ключ Mistral. Проверьте настройки.")
    if "rate limit" in error_str or "429" in error_str:
        logger.error(f"Mistral rate limit error: {error}")
        return RateLimitError("Превышен лимит запросов Mistral. Попробуйте позже.")
    if "not found" in error_str or "404" in error_str:
        logger.error(f"Mistral model not found: {error}")
        return ModelNotFoundError(f"Модель {model} не найдена. Обновите список моделей.")
    if "timeout" in error_str or "connection" in error_str:
        logger.error(f"Mistral network error: {error}")
        return NetworkError("Ошибка сети при подключении к Mistral.")
    logger.error(f"Mistral unexpected error: {error}")
    return ProviderError(f"Ошибка провайдера Mistral: {error}")


@ProviderFactory.register(name="mistral", default_model="mistral-large-latest")
class MistralProvider(BaseLLMProvider):
    """Mistral AI provider with native SDK support.

    Uses the official mistralai SDK with synchronous streaming
    wrapped in asyncio.to_thread for non-blocking operation.
    """

    def __init__(self, api_key: str, model: str = "mistral-large-latest", **kwargs):
        """Initialize Mistral provider.

        Args:
            api_key: Mistral API key.
            model: Model identifier.
        """
        self._client = Mistral(api_key=api_key)
        self.model = model

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion using Mistral native API.

        Args:
            request: Chat request with messages and parameters.

        Yields:
            Token strings from the API.

        Raises:
            AuthenticationError: Invalid API key.
            RateLimitError: Rate limit exceeded.
            ModelNotFoundError: Model not available.
            NetworkError: Connection issues.
            ProviderError: Other failures.
        """
        try:
            messages = []
            for msg in request.messages:
                content = msg.content
                if isinstance(content, list):
                    content = await to_mistral_content(content)
                messages.append({"role": msg.role, "content": content})

            if request.system_prompt:
                messages.insert(0, {"role": "system", "content": request.system_prompt})

            def _stream():
                return self._client.chat.stream(
                    model=self.model,
                    messages=messages,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                )

            stream_response = await asyncio.to_thread(_stream)

            for chunk in stream_response:
                if chunk.data.choices[0].delta.content:
                    yield chunk.data.choices[0].delta.content

        except (
            AuthenticationError,
            RateLimitError,
            ModelNotFoundError,
            NetworkError,
            ProviderError,
        ):
            raise
        except Exception as e:
            raise _map_mistral_error(e, self.model) from e

    async def health_check(self) -> bool:
        """Check if Mistral API is accessible."""
        try:

            def _check():
                return self._client.chat.complete(
                    model=self.model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=10,
                )

            await asyncio.to_thread(_check)
            return True
        except Exception as e:
            logger.warning(f"Mistral health check failed: {e}")
            return False

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=True,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=["jpg", "jpeg", "png", "gif", "webp"],
            max_context_tokens=128000,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=True,
            has_models_list=True,
            free_tier_available=True,
        )

    async def list_models(self) -> List[ModelInfo]:
        try:

            def _list():
                return self._client.models.list()

            models = await asyncio.to_thread(_list)
            result = []
            for model in models.data:
                result.append(
                    ModelInfo(
                        id=model.id,
                        name=model.id,
                        context_length=getattr(model, "context_length", 4096),
                        pricing=None,
                        free_tier=True,
                    )
                )
            return result
        except Exception as e:
            logger.error(f"[Mistral] Failed to list models: {e}")
            return []
