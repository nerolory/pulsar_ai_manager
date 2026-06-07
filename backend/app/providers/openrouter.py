from app.providers.openai_compatible import OpenAICompatibleProvider
from app.schemas import ProviderCapabilities
from app.utils import NumberUtils
import httpx
from loguru import logger


class OpenRouterProvider(OpenAICompatibleProvider):
    """OpenRouter provider using OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str = "qwen/qwen3-235b-a22b:free"):
        super().__init__(api_key, model, "https://openrouter.ai/api/v1")

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
        """OpenRouter has free models with zero prompt price."""
        pricing = getattr(model, 'pricing', None)
        return pricing and 'prompt' in pricing and float(pricing['prompt']) == 0

    async def check_balance(self) -> dict | None:
        """Check OpenRouter account balance."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://openrouter.ai/api/v1/credits",
                    headers={"Authorization": f"Bearer {self._client.api_key}"}
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
                        "currency": "USD"
                    }
        except Exception as e:
            logger.error(f"[OpenRouter] Failed to check balance: {e}")
        return None
