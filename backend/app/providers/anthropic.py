"""Anthropic Claude provider using native SDK."""

from typing import AsyncIterator
import anthropic
from app.providers.base import BaseLLMProvider
from app.schemas import ChatRequest, ChatMessage
from app.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError,
    ProviderUnavailableError,
    ProviderError,
)
from loguru import logger


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider with native SDK support."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
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
