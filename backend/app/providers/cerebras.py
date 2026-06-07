"""Cerebras provider using OpenAI-compatible API."""

from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.factory import ProviderFactory
from app.schemas import ProviderCapabilities


@ProviderFactory.register(name="cerebras", default_model="llama3.1-70b")
class CerebrasProvider(OpenAICompatibleProvider):
    """Cerebras provider — high-speed inference.

    Inherits unified error handling from OpenAICompatibleProvider.
    """

    def __init__(self, api_key: str, model: str = "llama3.1-70b", **kwargs):
        """Initialize Cerebras provider.

        Args:
            api_key: Cerebras API key.
            model: Model identifier.
        """
        super().__init__(api_key, model, "https://api.cerebras.ai/v1")

    def get_capabilities(self) -> ProviderCapabilities:
        """Return Cerebras-specific capabilities."""
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=False,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=[],
            max_context_tokens=32000,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=False,
            has_models_list=True,
            free_tier_available=True,
        )

    def _is_free_tier(self, model) -> bool:
        """Cerebras has free tier for all models."""
        return True
