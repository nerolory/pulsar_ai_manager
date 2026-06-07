"""Base class for OpenAI-compatible LLM providers.

Provides unified chat streaming, error handling, health checks,
model listing and capability reporting for all OpenAI-compatible APIs.
"""

from typing import AsyncIterator, List
import httpx
from openai import AsyncOpenAI
from loguru import logger

from app.providers.base import BaseLLMProvider
from app.schemas import ChatRequest, ProviderCapabilities, ModelInfo
from app.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError,
    ProviderError,
)


class OpenAICompatibleProvider(BaseLLMProvider):
    """Base class for providers using OpenAI-compatible API.

    This class provides common functionality for providers that use the
    OpenAI API format, including model listing, capabilities, and
    unified error handling so subclasses don't need to duplicate it.

    Attributes:
        model: Currently active model identifier.
    """

    def __init__(self, api_key: str, model: str, base_url: str):
        """Initialize provider with API credentials.

        Args:
            api_key: Authentication key for the provider.
            model: Model identifier to use for completions.
            base_url: Base URL of the OpenAI-compatible API.
        """
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.AsyncClient(trust_env=False),
        )
        self.model = model
        self._provider_name = self.__class__.__name__.replace("Provider", "").lower()

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion with unified error handling.

        Args:
            request: Chat request with messages and parameters.

        Yields:
            Token strings as they arrive from the API.

        Raises:
            AuthenticationError: Invalid API key.
            RateLimitError: Rate limit exceeded.
            ModelNotFoundError: Model not available.
            NetworkError: Connection/timeout issues.
            ProviderError: Any other provider failure.
        """
        try:
            messages = [
                {
                    "role": message.role,
                    "content": (
                        message.content
                        if isinstance(message.content, str)
                        else [part.model_dump(exclude_none=True) for part in message.content]
                    ),
                }
                for message in request.messages
            ]

            stream = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    if hasattr(choice, "delta") and hasattr(choice.delta, "content"):
                        token = choice.delta.content
                        if token:
                            yield token
        except (
            AuthenticationError,
            RateLimitError,
            ModelNotFoundError,
            NetworkError,
            ProviderError,
        ):
            raise
        except Exception as e:
            raise self._map_error(e) from e

    def _map_error(self, error: Exception) -> ProviderError:
        """Map a raw exception to the appropriate typed ProviderError.

        Args:
            error: The original exception from the API call.

        Returns:
            A typed exception subclass for the error category.
        """
        error_str = str(error).lower()
        name = self._provider_name.capitalize()

        if "authentication" in error_str or "invalid api key" in error_str or "401" in error_str:
            logger.error(f"{name} authentication error: {error}")
            return AuthenticationError(f"Неверный API ключ {name}. Проверьте настройки.")
        if "rate limit" in error_str or "429" in error_str:
            logger.error(f"{name} rate limit error: {error}")
            return RateLimitError(f"Превышен лимит запросов {name}. Попробуйте позже.")
        if "not found" in error_str or "404" in error_str:
            logger.error(f"{name} model not found: {error}")
            return ModelNotFoundError(f"Модель {self.model} не найдена. Обновите список моделей.")
        if "timeout" in error_str or "connection" in error_str:
            logger.error(f"{name} network error: {error}")
            return NetworkError(f"Ошибка сети при подключении к {name}.")

        logger.error(f"{name} unexpected error: {error}")
        return ProviderError(f"Ошибка провайдера {name}: {error}")

    async def health_check(self) -> bool:
        """Check if provider API is accessible."""
        try:
            models = await self._client.models.list()
            return len(models.data) > 0
        except Exception as e:
            logger.warning(f"{self._provider_name} health check failed: {e}")
            return False

    def get_capabilities(self) -> ProviderCapabilities:
        """Return provider capabilities. Override in subclass for custom values."""
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=False,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=[],
            max_context_tokens=4096,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=False,
            has_models_list=True,
            free_tier_available=False,
        )

    async def list_models(self) -> List[ModelInfo]:
        """Return list of available models from OpenAI-compatible API."""
        try:
            models = await self._client.models.list()
            result = []
            for model in models.data:
                model_info = ModelInfo(
                    id=model.id,
                    name=getattr(model, "name", model.id),
                    context_length=getattr(model, "context_length", 4096),
                    pricing=getattr(model, "pricing", None),
                    free_tier=self._is_free_tier(model),
                )

                # Add dynamic limit information if available
                limit_info = self._get_model_limit(model)
                if limit_info:
                    if "daily_limit" in limit_info:
                        model_info.daily_limit = limit_info["daily_limit"]
                    if "limit_tokens" in limit_info:
                        model_info.limit_tokens = limit_info["limit_tokens"]
                    if "is_free" in limit_info:
                        model_info.is_free = limit_info["is_free"]

                result.append(model_info)
            return result
        except Exception as e:
            logger.error(f"[{self._provider_name}] Failed to list models: {e}")
            return []

    def _is_free_tier(self, model) -> bool:
        """Determine if model has free tier. Override in subclass for custom logic."""
        return False

    def _get_model_limit(self, model) -> dict | None:
        """Extract model limit information from API data. Override in subclass."""
        return None

    async def check_balance(self) -> dict | None:
        """Check account balance. Not supported by default OpenAI-compatible API."""
        return None
