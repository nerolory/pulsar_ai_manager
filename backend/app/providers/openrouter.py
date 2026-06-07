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
        """OpenRouter has free models with zero prompt price or (free) in name."""
        pricing = getattr(model, 'pricing', None)
        model_id = getattr(model, 'id', '')
        
        # Check if price is zero
        if pricing and 'prompt' in pricing and float(pricing['prompt']) == 0:
            return True
        
        # Check if model name contains free indicator
        if ':free' in model_id.lower() or '(free)' in model_id.lower():
            return True
        
        return False

    def _get_model_limit(self, model) -> dict | None:
        """Extract model limit information from pricing data."""
        pricing = getattr(model, 'pricing', None)
        logger.info(f"[OpenRouter] Model {getattr(model, 'id', 'unknown')} pricing: {pricing}")
        
        if not pricing:
            return None
        
        limit_info = {}
        
        # Check for request limit (daily_limit)
        if 'request' in pricing:
            request_limit = pricing.get('request')
            if request_limit == 0:
                limit_info['daily_limit'] = None  # Unlimited
            else:
                limit_info['daily_limit'] = int(request_limit)
        
        # Check for token limits and payment status
        if 'prompt' in pricing and 'completion' in pricing:
            prompt_price = float(pricing['prompt'])
            completion_price = float(pricing['completion'])
            
            if prompt_price == 0 and completion_price == 0:
                limit_info['is_free'] = True
                limit_info['requires_payment'] = False
                # Try to get limit from pricing description or other metadata
                description = getattr(model, 'description', '')
                if 'free' in description.lower() or 'limit' in description.lower():
                    # Parse limit from description if available
                    import re
                    limit_match = re.search(r'(\d+)\s*(requests?|tokens?)', description.lower())
                    if limit_match:
                        limit_value = int(limit_match.group(1))
                        unit = limit_match.group(2)
                        if 'request' in unit:
                            limit_info['daily_limit'] = limit_value
                        elif 'token' in unit:
                            limit_info['limit_tokens'] = limit_value
            else:
                # Model has pricing, so it requires payment
                limit_info['requires_payment'] = True
                limit_info['is_free'] = False
        
        logger.info(f"[OpenRouter] Model {getattr(model, 'id', 'unknown')} limit_info: {limit_info}")
        return limit_info if limit_info else None

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
