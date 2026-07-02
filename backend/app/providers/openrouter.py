"""OpenRouter provider using OpenAI-compatible API."""

import re
from typing import AsyncIterator

import httpx
from loguru import logger

from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.factory import ProviderFactory
from app.providers.media_utils import to_openai_content
from app.schemas import ChatRequest, ProviderCapabilities
from app.utils import NumberUtils
from app.exceptions import (
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError,
    ProviderError,
)

_SAFETY_MODEL_MARKERS = ("content-safety", "nemotron", "safety-router")
_SAFETY_TEXT_PREFIXES = ("user safety:", "content policy:", "assistant safety:")


@ProviderFactory.register(name="openrouter", default_model="qwen/qwen3-235b-a22b:free")
class OpenRouterProvider(OpenAICompatibleProvider):
    """OpenRouter provider — 200+ models, free tier available.

    Inherits unified error handling from OpenAICompatibleProvider.
    Adds balance checking and free tier detection.
    """

    def __init__(self, api_key: str, model: str = "qwen/qwen3-235b-a22b:free", base_url: str | None = None, **kwargs):
        """Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key (sk-or-v1-...).
            model: Model identifier.
            base_url: Optional custom API base URL.
        """
        super().__init__(api_key, model, base_url or "https://openrouter.ai/api/v1")

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion, filtering OpenRouter safety-router chunks."""
        try:
            async for token in self._stream_tokens(request):
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

    def _is_safety_chunk(self, chunk) -> bool:
        model = (getattr(chunk, "model", None) or "").lower()
        return any(marker in model for marker in _SAFETY_MODEL_MARKERS)

    def _is_safety_token(self, token: str) -> bool:
        normalized = token.strip().lower()
        return any(normalized.startswith(prefix) for prefix in _SAFETY_TEXT_PREFIXES)

    async def _stream_tokens(self, request: ChatRequest) -> AsyncIterator[str]:
        """Internal stream with safety chunk filtering by model field."""
        messages = []
        for message in request.messages:
            content = message.content
            if isinstance(content, list):
                content = await to_openai_content(content)
            messages.append({"role": message.role, "content": content})

        stream = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if self._is_safety_chunk(chunk):
                continue
            if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                choice = chunk.choices[0]
                if hasattr(choice, "delta") and hasattr(choice.delta, "content"):
                    token = choice.delta.content
                    if token and not self._is_safety_token(token):
                        yield token

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=True,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=["jpg", "jpeg", "png", "gif", "webp"],
            max_context_tokens=200000,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=True,
            has_models_list=True,
            free_tier_available=True,
        )

    def _is_free_tier(self, model) -> bool:
        """OpenRouter has free models with zero prompt price or (free) in name."""
        pricing = getattr(model, "pricing", None)
        model_id = getattr(model, "id", "")

        # Check if price is zero
        if pricing and "prompt" in pricing and float(pricing["prompt"]) == 0:
            return True

        # Check if model name contains free indicator
        if ":free" in model_id.lower() or "(free)" in model_id.lower():
            return True

        return False

    def _get_model_limit(self, model) -> dict | None:
        """Extract model limit information from pricing data."""
        pricing = getattr(model, "pricing", None)
        logger.info(f"[OpenRouter] Model {getattr(model, 'id', 'unknown')} pricing: {pricing}")

        if not pricing:
            return None

        limit_info = {}

        # Check for request limit (daily_limit)
        if "request" in pricing:
            request_limit = pricing.get("request")
            if request_limit == 0:
                limit_info["daily_limit"] = None  # Unlimited
            else:
                limit_info["daily_limit"] = int(request_limit)

        # Check for token limits and payment status
        if "prompt" in pricing and "completion" in pricing:
            prompt_price = float(pricing["prompt"])
            completion_price = float(pricing["completion"])

            if prompt_price == 0 and completion_price == 0:
                limit_info["is_free"] = True
                limit_info["requires_payment"] = False
                # Try to get limit from pricing description or other metadata
                description = getattr(model, "description", "")
                if "free" in description.lower() or "limit" in description.lower():
                    limit_match = re.search(r"(\d+)\s*(requests?|tokens?)", description.lower())
                    if limit_match:
                        limit_value = int(limit_match.group(1))
                        unit = limit_match.group(2)
                        if "request" in unit:
                            limit_info["daily_limit"] = limit_value
                        elif "token" in unit:
                            limit_info["limit_tokens"] = limit_value
            else:
                # Model has pricing, so it requires payment
                limit_info["requires_payment"] = True
                limit_info["is_free"] = False

        logger.info(
            f"[OpenRouter] Model {getattr(model, 'id', 'unknown')} limit_info: {limit_info}"
        )
        return limit_info if limit_info else None

    async def check_balance(self) -> dict | None:
        """Check OpenRouter account balance."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://openrouter.ai/api/v1/credits",
                    headers={"Authorization": f"Bearer {self._client.api_key}"},
                )
                if response.status_code == 200:
                    data = response.json()
                    total_credits = data.get("data", {}).get("total_credits", 0)
                    total_usage = data.get("data", {}).get("total_usage", 0)
                    remaining = total_credits - total_usage
                    remaining = NumberUtils.ensure_non_negative(remaining)
                    return {
                        "balance": NumberUtils.format_currency(remaining),
                        "total_credits": NumberUtils.format_currency(total_credits),
                        "total_usage": NumberUtils.format_currency(total_usage),
                        "currency": "USD",
                    }
        except Exception as e:
            logger.error(f"[OpenRouter] Failed to check balance: {e}")
        return None
