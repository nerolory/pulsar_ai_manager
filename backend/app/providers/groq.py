"""Groq provider using OpenAI-compatible API."""

from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.factory import ProviderFactory
from app.schemas import ProviderCapabilities


@ProviderFactory.register(name="groq", default_model="llama-3.1-70b-versatile")
class GroqProvider(OpenAICompatibleProvider):
    """Groq provider — ultra-fast inference for Llama, Mixtral models.

    Inherits unified error handling from OpenAICompatibleProvider.
    """

    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile", base_url: str | None = None, **kwargs):
        """Initialize Groq provider.

        Args:
            api_key: Groq API key (gsk_...).
            model: Model identifier.
            base_url: Optional custom API base URL.
        """
        super().__init__(api_key, model, base_url or "https://api.groq.com/openai/v1")

    def get_capabilities(self) -> ProviderCapabilities:
        """Return Groq-specific capabilities."""
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=False,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=[],
            max_context_tokens=131072,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=False,
            has_models_list=True,
            free_tier_available=True,
        )

    def _is_free_tier(self, model) -> bool:
        """Groq has free tier for all models."""
        return True
