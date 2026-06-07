"""Qwen provider using OpenAI-compatible API (Alibaba Cloud)."""

from typing import AsyncIterator
from openai import AsyncOpenAI
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


class QwenProvider(BaseLLMProvider):
    """Qwen provider with OpenAI-compatible API (Alibaba Cloud)."""

    def __init__(self, api_key: str, model: str = "qwen-max"):
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = model

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion using Qwen API."""
        try:
            # Convert messages to OpenAI format
            messages = []
            for msg in request.messages:
                if msg.role == "system":
                    messages.append({"role": "system", "content": msg.content})
                else:
                    messages.append({"role": msg.role, "content": msg.content})

            # Add system prompt if provided
            if request.system_prompt:
                messages.insert(0, {"role": "system", "content": request.system_prompt})

            # Stream response
            stream = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

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

    async def health_check(self) -> bool:
        """Check if Qwen API is accessible."""
        try:
            await self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.warning(f"Qwen health check failed: {e}")
            return False
