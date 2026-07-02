"""Google Gemini provider using native SDK."""

import asyncio
import base64
from typing import AsyncIterator, List, Union

import google.generativeai as genai
from loguru import logger

from app.providers.base import BaseLLMProvider
from app.providers.factory import ProviderFactory
from app.providers.media_utils import resolve_image_base64
from app.schemas import ChatRequest, ProviderCapabilities, ModelInfo, ContentPart
from app.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError,
    ProviderError,
)


def _map_gemini_error(error: Exception, model_name: str) -> ProviderError:
    """Map a Gemini exception to a typed ProviderError."""
    error_str = str(error).lower()
    if "authentication" in error_str or "invalid api key" in error_str or "permission" in error_str:
        logger.error(f"Gemini authentication error: {error}")
        return AuthenticationError("auth_error_gemini")
    if "rate limit" in error_str or "429" in error_str or "quota" in error_str:
        logger.error(f"Gemini rate limit error: {error}")
        return RateLimitError("rate_limit_error_gemini")
    if "not found" in error_str or "404" in error_str:
        logger.error(f"Gemini model not found: {error}")
        return ModelNotFoundError(f"model_not_found_gemini:{model_name}")
    if "timeout" in error_str or "connection" in error_str or "network" in error_str:
        logger.error(f"Gemini network error: {error}")
        return NetworkError("network_error_gemini")
    logger.error(f"Gemini unexpected error: {error}")
    return ProviderError(f"provider_error_gemini:{error}")


@ProviderFactory.register(name="gemini", default_model="gemini-2.0-flash-exp")
class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider with native SDK support."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp", **kwargs):
        genai.configure(api_key=api_key)
        self.model = model
        self._genai_model = genai.GenerativeModel(model)

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion using Gemini native API."""
        try:
            system_prompt = request.system_prompt
            history: list[dict] = []

            for msg in request.messages:
                if msg.role == "system":
                    system_prompt = (
                        msg.content if isinstance(msg.content, str) else str(msg.content)
                    )
                else:
                    role = "user" if msg.role == "user" else "model"
                    parts = await self._to_gemini_parts(msg.content)
                    history.append({"role": role, "parts": parts})

            if system_prompt:
                model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
            else:
                model = self._genai_model

            generation_config = genai.types.GenerationConfig(
                temperature=request.temperature,
                top_p=request.top_p,
                max_output_tokens=request.max_tokens,
            )

            def _stream():
                if not history:
                    return model.generate_content(
                        "",
                        generation_config=generation_config,
                        stream=True,
                    )
                if len(history) == 1:
                    return model.generate_content(
                        history[0]["parts"],
                        generation_config=generation_config,
                        stream=True,
                    )
                last = history[-1]
                previous = history[:-1]
                chat = model.start_chat(history=previous)
                return chat.send_message(
                    last["parts"],
                    generation_config=generation_config,
                    stream=True,
                )

            response = await asyncio.to_thread(_stream)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except (
            AuthenticationError,
            RateLimitError,
            ModelNotFoundError,
            NetworkError,
            ProviderError,
        ):
            raise
        except Exception as e:
            raise _map_gemini_error(e, self.model) from e

    async def _to_gemini_parts(self, content: Union[str, List[ContentPart]]) -> list:
        if isinstance(content, str):
            return [content]

        parts = []
        for part in content:
            if part.type == "text":
                parts.append(part.text or "")
            elif part.type == "image_url" and part.image_url:
                media_type, data = await resolve_image_base64(part.image_url.url)
                parts.append(
                    {
                        "mime_type": media_type,
                        "data": base64.b64decode(data),
                    }
                )
        return parts

    async def health_check(self) -> bool:
        """Check if Gemini API is accessible."""
        try:

            def _check():
                return self._genai_model.generate_content("test", max_output_tokens=10)

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
                if "generateContent" in model.supported_generation_methods:
                    result.append(
                        ModelInfo(
                            id=model.name,
                            name=model.display_name or model.name,
                            context_length=getattr(model, "context_length", 4096),
                            pricing=None,
                            free_tier=True,
                        )
                    )
            return result
        except Exception as e:
            logger.error(f"[Gemini] Failed to list models: {e}")
            return []
