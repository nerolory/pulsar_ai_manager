"""Qwen provider using OpenAI-compatible API (Alibaba Cloud)."""

from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.factory import ProviderFactory
from app.schemas import ProviderCapabilities


@ProviderFactory.register(name="qwen", default_model="qwen-max")
class QwenProvider(OpenAICompatibleProvider):
    """Qwen provider — Alibaba Cloud models (Qwen 3, Qwen Max).

    Inherits unified error handling from OpenAICompatibleProvider.
    """

    def __init__(self, api_key: str, model: str = "qwen-max", base_url: str | None = None, **kwargs):
        """Initialize Qwen provider.

        Args:
            api_key: Alibaba Cloud DashScope API key.
            model: Model identifier.
            base_url: Optional custom API base URL.
        """
        super().__init__(
            api_key,
            model,
            base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def get_capabilities(self) -> ProviderCapabilities:
        """Return Qwen-specific capabilities."""
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=True,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=["jpg", "jpeg", "png", "gif", "webp"],
            max_context_tokens=32000,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=True,
            has_models_list=True,
            free_tier_available=True,
        )

    def _is_free_tier(self, model) -> bool:
        """Qwen has free tier for all models."""
        return True
