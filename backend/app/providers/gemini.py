"""Google Gemini provider using native SDK."""

from typing import AsyncIterator, List
import asyncio
import google.generativeai as genai
from app.providers.base import BaseLLMProvider
from app.schemas import ChatRequest, ProviderCapabilities, ModelInfo
from app.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError,
    ProviderUnavailableError,
    ProviderError,
)
from loguru import logger


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider with native SDK support."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        self.model_name = model

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion using Gemini native API."""
        try:
            # Convert messages to Gemini format
            messages = []
            system_prompt = request.system_prompt

            for msg in request.messages:
                if msg.role == "system":
                    system_prompt = msg.content if isinstance(msg.content, str) else str(msg.content)
                elif msg.role == "user":
                    messages.append(msg.content if isinstance(msg.content, str) else str(msg.content))
                elif msg.role == "assistant":
                    messages.append(f"Assistant: {msg.content}")

            # Combine messages into a single prompt for Gemini
            prompt = "\n".join(messages)

            # Set generation config
            generation_config = genai.types.GenerationConfig(
                temperature=request.temperature,
                top_p=request.top_p,
                max_output_tokens=request.max_tokens,
            )

            # Stream response (run in thread to avoid blocking)
            def _stream():
                return self._model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    stream=True,
                )

            response = await asyncio.to_thread(_stream)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            error_str = str(e).lower()
            if "authentication" in error_str or "invalid api key" in error_str or "permission" in error_str:
                logger.error(f"Gemini authentication error: {e}")
                raise AuthenticationError("Неверный API ключ Gemini. Проверьте настройки.")
            elif "rate limit" in error_str or "429" in error_str or "quota" in error_str:
                logger.error(f"Gemini rate limit error: {e}")
                raise RateLimitError("Превышен лимит запросов Gemini. Попробуйте позже.")
            elif "not found" in error_str or "404" in error_str:
                logger.error(f"Gemini model not found: {e}")
                raise ModelNotFoundError(f"Модель {self.model_name} не найдена. Обновите список моделей.")
            elif "timeout" in error_str or "connection" in error_str or "network" in error_str:
                logger.error(f"Gemini network error: {e}")
                raise NetworkError("Ошибка сети при подключении к Gemini.")
            else:
                logger.error(f"Gemini unexpected error: {e}")
                raise ProviderError(f"Ошибка провайдера Gemini: {str(e)}")

    async def health_check(self) -> bool:
        """Check if Gemini API is accessible."""
        try:
            def _check():
                return self._model.generate_content("test", max_output_tokens=10)
            await asyncio.to_thread(_check)
            return True
        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")
            return False

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=True,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=["jpg", "jpeg", "png", "gif", "webp"],
            max_context_tokens=2800000,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=True,
            has_models_list=True,
            free_tier_available=True,
        )

    async def list_models(self) -> List[ModelInfo]:
        try:
            def _list():
                return genai.list_models()
            models = await asyncio.to_thread(_list)
            result = []
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    result.append(ModelInfo(
                        id=model.name,
                        name=model.display_name or model.name,
                        context_length=getattr(model, 'context_length', 4096),
                        pricing=None,
                        free_tier=True,
                    ))
            return result
        except Exception as e:
            logger.error(f"[Gemini] Failed to list models: {e}")
            return []
