"""VseLLM provider using OpenAI-compatible API."""

from loguru import logger

from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.factory import ProviderFactory
from app.schemas import ChatRequest, ProviderCapabilities


@ProviderFactory.register(name="vsellm", default_model="openai/gpt-4o-mini")
class VseLLMProvider(OpenAICompatibleProvider):
    """VseLLM provider — GPT-4o, Claude, Gemini via api.vsellm.ru.

    Inherits unified error handling from OpenAICompatibleProvider.
    Adds multimodal message logging.
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini", **kwargs):
        """Initialize VseLLM provider.

        Args:
            api_key: VseLLM API key (sk-...).
            model: Model identifier.
        """
        super().__init__(api_key, model, "https://api.vsellm.ru/v1")

    async def chat(self, request: ChatRequest):
        """Stream chat completion with multimodal logging.

        Args:
            request: Chat request with messages and parameters.

        Yields:
            Token strings from the API.
        """
        for message in request.messages:
            if isinstance(message.content, list):
                logger.info(f"[VseLLM] multimodal msg parts: {[p.type for p in message.content]}")
            else:
                logger.info(f"[VseLLM] text msg len={len(message.content)}")
        async for token in super().chat(request):
            yield token

    def get_capabilities(self) -> ProviderCapabilities:
        """Return VseLLM-specific capabilities."""
        return ProviderCapabilities(
            supports_caching=True,
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

    async def check_balance(self) -> dict | None:
        """VseLLM doesn't provide public balance API."""
        return None
