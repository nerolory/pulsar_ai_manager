"""OpenAI provider using OpenAI-compatible API."""

from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.factory import ProviderFactory
from app.schemas import ProviderCapabilities

DEFAULT_BASE_URL = "https://api.openai.com/v1"


@ProviderFactory.register(name="openai", default_model="gpt-4o-mini")
class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI provider — GPT-4o, GPT-4.1, o-series models."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
        **kwargs,
    ):
        super().__init__(api_key, model, base_url or DEFAULT_BASE_URL)

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=True,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=["jpg", "jpeg", "png", "gif", "webp"],
            max_context_tokens=128000,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=False,
            has_models_list=True,
            free_tier_available=False,
        )
