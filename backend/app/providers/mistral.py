"""Mistral AI provider using native SDK."""

from typing import AsyncIterator
import asyncio
from mistralai import Mistral
from app.providers.base import BaseLLMProvider
from app.schemas import ChatRequest
from app.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError,
    ProviderUnavailableError,
    ProviderError,
)
from loguru import logger


class MistralProvider(BaseLLMProvider):
    """Mistral AI provider with native SDK support."""

    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        self._client = Mistral(api_key=api_key)
        self.model = model

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion using Mistral native API."""
        try:
            # Convert messages to Mistral format
            messages = []
            for msg in request.messages:
                if msg.role == "system":
                    messages.append({"role": "system", "content": msg.content})
                else:
                    messages.append({"role": msg.role, "content": msg.content})

            # Add system prompt if provided
            if request.system_prompt:
                messages.insert(0, {"role": "system", "content": request.system_prompt})

            # Stream response (run in thread to avoid blocking)
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

        except Exception as e:
            error_str = str(e).lower()
            if "authentication" in error_str or "invalid api key" in error_str:
                logger.error(f"Mistral authentication error: {e}")
                raise AuthenticationError("Неверный API ключ Mistral. Проверьте настройки.")
            elif "rate limit" in error_str or "429" in error_str:
                logger.error(f"Mistral rate limit error: {e}")
                raise RateLimitError("Превышен лимит запросов Mistral. Попробуйте позже.")
            elif "not found" in error_str or "404" in error_str:
                logger.error(f"Mistral model not found: {e}")
                raise ModelNotFoundError(f"Модель {self.model} не найдена. Обновите список моделей.")
            elif "timeout" in error_str or "connection" in error_str:
                logger.error(f"Mistral network error: {e}")
                raise NetworkError("Ошибка сети при подключении к Mistral.")
            else:
                logger.error(f"Mistral unexpected error: {e}")
                raise ProviderError(f"Ошибка провайдера Mistral: {str(e)}")

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
