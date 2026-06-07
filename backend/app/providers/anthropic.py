"""Anthropic Claude provider using native SDK."""

from typing import AsyncIterator, List

import anthropic
from loguru import logger

from app.providers.base import BaseLLMProvider
from app.providers.factory import ProviderFactory
from app.schemas import ChatRequest, ProviderCapabilities, ModelInfo
from app.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError,
    ProviderUnavailableError,
    ProviderError,
)


@ProviderFactory.register(name="anthropic", default_model="claude-3-5-sonnet-20241022")
class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider with native SDK support.

    Uses the official anthropic async SDK for streaming.
    Error handling uses SDK-specific exception types for precise mapping.
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (sk-ant-...).
            model: Model identifier.
        """
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion using Anthropic native API."""
        try:
            # Convert messages to Anthropic format
            messages = []
            system_prompt = None
            
            for msg in request.messages:
                if msg.role == "system":
                    system_prompt = msg.content if isinstance(msg.content, str) else str(msg.content)
                else:
                    # Convert content to Anthropic format
                    if isinstance(msg.content, str):
                        messages.append({"role": msg.role, "content": msg.content})
                    else:
                        # Handle multimodal content
                        content = []
                        for part in msg.content:
                            if part.type == "text":
                                content.append({"type": "text", "text": part.text})
                            elif part.type == "image_url":
                                content.append({
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": part.image_url.url,
                                    }
                                })
                        messages.append({"role": msg.role, "content": content})

            # If system_prompt is provided in request, use it
            if request.system_prompt:
                system_prompt = request.system_prompt

            # Stream response
            async with self._client.messages.stream(
                model=self.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                system=system_prompt,
                messages=messages if messages else [],
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except anthropic.AuthenticationError as e:
            logger.error(f"Anthropic authentication error: {e}")
            raise AuthenticationError("Неверный API ключ Anthropic. Проверьте настройки.")
        except anthropic.RateLimitError as e:
            logger.error(f"Anthropic rate limit error: {e}")
            raise RateLimitError("Превышен лимит запросов Anthropic. Попробуйте позже.")
        except anthropic.NotFoundError as e:
            logger.error(f"Anthropic model not found: {e}")
            raise ModelNotFoundError(f"Модель {self.model} не найдена. Обновите список моделей.")
        except anthropic.APITimeoutError as e:
            logger.error(f"Anthropic timeout error: {e}")
            raise NetworkError("Таймаут запроса к Anthropic. Проверьте подключение к интернету.")
        except anthropic.APIConnectionError as e:
            logger.error(f"Anthropic connection error: {e}")
            raise NetworkError("Ошибка сети при подключении к Anthropic.")
        except anthropic.APIStatusError as e:
            logger.error(f"Anthropic status error: {e}")
            raise ProviderUnavailableError("Сервис Anthropic временно недоступен.")
        except Exception as e:
            logger.error(f"Anthropic unexpected error: {e}")
            raise ProviderError(f"Ошибка провайдера Anthropic: {str(e)}")

    async def health_check(self) -> bool:
        """Check if Anthropic API is accessible."""
        try:
            await self._client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}],
            )
            return True
        except Exception as e:
            logger.warning(f"Anthropic health check failed: {e}")
            return False

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=True,
            supports_images=True,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=["jpg", "jpeg", "png", "gif", "webp"],
            max_context_tokens=200000,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=True,
            has_models_list=True,
            free_tier_available=False,
        )

    async def list_models(self) -> List[ModelInfo]:
        try:
            models = await self._client.models.list()
            result = []
            for model in models.data:
                result.append(ModelInfo(
                    id=model.id,
                    name=model.id,
                    context_length=getattr(model, 'context_length', 4096),
                    pricing=None,
                    free_tier=False,
                ))
            return result
        except Exception as e:
            logger.error(f"[Anthropic] Failed to list models: {e}")
            return []
