"""GigaChat provider using the official Sber GigaChat SDK."""

from __future__ import annotations

import os
from typing import AsyncIterator, List

from gigachat import GigaChat
from gigachat.exceptions import AuthenticationError as GigaAuthError
from gigachat.exceptions import ResponseError
from gigachat.models import Chat, Messages, MessagesRole
from loguru import logger

from app.exceptions import (
    AuthenticationError,
    ModelNotFoundError,
    NetworkError,
    ProviderError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.providers.base import BaseLLMProvider
from app.providers.factory import ProviderFactory
from app.schemas import ChatRequest, ModelInfo, ProviderCapabilities

DEFAULT_BASE_URL = "https://gigachat.devices.sberbank.ru/api/v1"
DEFAULT_MODEL = "GigaChat"


def _map_gigachat_error(error: Exception, model: str) -> ProviderError:
    error_str = str(error).lower()
    if isinstance(error, GigaAuthError) or "401" in error_str or "authentication" in error_str:
        return AuthenticationError("auth_error_provider:GigaChat")
    if "429" in error_str or "rate limit" in error_str:
        return RateLimitError("rate_limit_error_provider:GigaChat")
    if "404" in error_str or "not found" in error_str:
        return ModelNotFoundError(f"model_not_found_provider:{model}")
    if "timeout" in error_str or "connection" in error_str:
        return NetworkError("network_error_provider:GigaChat")
    if isinstance(error, ResponseError):
        status = getattr(error, "status_code", None)
        if status == 503:
            return ProviderUnavailableError("provider_unavailable:GigaChat")
    return ProviderError(f"provider_error_generic:GigaChat:{error}")


@ProviderFactory.register(name="gigachat", default_model=DEFAULT_MODEL)
class GigaChatProvider(BaseLLMProvider):
    """GigaChat provider — Sber native API with OAuth credentials."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        base_url: str | None = None,
        **kwargs,
    ):
        verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() in (
            "1",
            "true",
            "yes",
        )
        self._client_kwargs = {
            "credentials": api_key,
            "base_url": base_url or DEFAULT_BASE_URL,
            "verify_ssl_certs": verify_ssl,
            "model": model or DEFAULT_MODEL,
        }
        self.model = model or DEFAULT_MODEL

    def _build_messages(self, request: ChatRequest) -> list[Messages]:
        messages: list[Messages] = []
        system_prompt = request.system_prompt

        for msg in request.messages:
            if msg.role == "system":
                system_prompt = msg.content if isinstance(msg.content, str) else str(msg.content)
            elif msg.role == "user":
                text = msg.content if isinstance(msg.content, str) else _parts_to_text(msg.content)
                messages.append(Messages(role=MessagesRole.USER, content=text))
            elif msg.role == "assistant":
                text = msg.content if isinstance(msg.content, str) else _parts_to_text(msg.content)
                messages.append(Messages(role=MessagesRole.ASSISTANT, content=text))

        if system_prompt:
            messages.insert(0, Messages(role=MessagesRole.SYSTEM, content=system_prompt))

        return messages

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        payload = Chat(
            model=self.model,
            messages=self._build_messages(request),
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
        )

        try:
            async with GigaChat(**self._client_kwargs) as client:
                async for chunk in client.astream(payload):
                    if not chunk.choices:
                        continue
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
        except (
            AuthenticationError,
            RateLimitError,
            ModelNotFoundError,
            NetworkError,
            ProviderUnavailableError,
            ProviderError,
        ):
            raise
        except Exception as e:
            logger.error(f"GigaChat stream error: {e}")
            raise _map_gigachat_error(e, self.model) from e

    async def health_check(self) -> bool:
        try:
            async with GigaChat(**self._client_kwargs) as client:
                response = await client.achat("ping")
                return bool(response.choices)
        except Exception as e:
            logger.warning(f"GigaChat health check failed: {e}")
            return False

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=False,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=[],
            max_context_tokens=32768,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=False,
            has_models_list=True,
            free_tier_available=False,
        )

    async def list_models(self) -> List[ModelInfo]:
        try:
            async with GigaChat(**self._client_kwargs) as client:
                models = await client.aget_models()
                return [
                    ModelInfo(
                        id=model.id_ or model.id or str(model),
                        name=model.id_ or model.id or str(model),
                        context_length=32768,
                        pricing=None,
                        free_tier=False,
                    )
                    for model in models.data
                ]
        except Exception as e:
            logger.error(f"[GigaChat] Failed to list models: {e}")
            return []


def _parts_to_text(parts) -> str:
    texts = [part.text for part in parts if getattr(part, "type", None) == "text" and part.text]
    return "\n".join(texts)
