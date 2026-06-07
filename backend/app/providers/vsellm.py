from app.providers.openai_compatible import OpenAICompatibleProvider
from app.schemas import ProviderCapabilities
from loguru import logger


class VseLLMProvider(OpenAICompatibleProvider):
    """VseLLM provider using OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini"):
        super().__init__(api_key, model, "https://api.vsellm.ru/v1")

    async def chat(self, request):
        """Stream chat completion with logging."""
        messages = [
            {"role": message.role, "content": message.content if isinstance(message.content, str) else [part.model_dump(exclude_none=True) for part in message.content]}
            for message in request.messages
        ]
        for message in messages:
            if isinstance(message["content"], list):
                logger.info(f"[VseLLM] multimodal msg parts: {[part['type'] for part in message['content']]}")
            else:
                logger.info(f"[VseLLM] text msg len={len(message['content'])}")
        async for token in super().chat(request):
            yield token

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=True,
            supports_images=True,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=["jpg", "jpeg", "png", "gif", "webp"],
            max_context_tokens=128000,
            streaming=True,
            pricing_model="per_token",
            has_balance_api=False,  # VseLLM doesn't provide public balance API
            has_models_list=True,
            free_tier_available=False,
        )

    async def check_balance(self) -> dict | None:
        """VseLLM doesn't provide public balance API. Check balance in personal cabinet."""
        return None
