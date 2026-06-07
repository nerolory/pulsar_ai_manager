"""Provider-related Pydantic schemas.

Defines capabilities and model information structures.
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class ProviderCapabilities(BaseModel):
    """Capabilities of an LLM provider.

    Attributes:
        supports_caching: Support for prompt caching.
        supports_images: Support for image inputs.
        supports_pdf: Support for PDF files.
        supports_system_prompt: Support for system prompts.
        supports_files: List of supported file formats.
        max_context_tokens: Maximum context window size.
        streaming: Support for streaming responses.
        pricing_model: Pricing model (per_token, per_request).
        has_balance_api: Has API for balance checking.
        has_models_list: Has API for listing models.
        free_tier_available: Has free tier available.
    """

    supports_caching: bool = False
    supports_images: bool = False
    supports_pdf: bool = False
    supports_system_prompt: bool = True
    supports_files: List[str] = Field(default_factory=list)
    max_context_tokens: int = 4096
    streaming: bool = True
    pricing_model: Literal["per_token", "per_request"] = "per_token"
    has_balance_api: bool = False
    has_models_list: bool = False
    free_tier_available: bool = False


class ModelInfo(BaseModel):
    """Information about a model.

    Attributes:
        id: Model identifier.
        name: Human-readable model name.
        context_length: Maximum context window.
        pricing: Pricing information (optional).
        free_tier: Whether free tier is available.
        is_free: Whether the model is completely free.
        daily_limit: Daily limit in requests/tokens.
        requires_payment: Whether payment is required.
        model_group_id: Group ID for free/paid versions.
        balance: Current balance for the model (optional).
        limit_period: Period for daily limit (day, month, etc.).
        limit_tokens: Token limit for the period.
        downloaded: Whether the model is downloaded (for local models).
        can_run: Whether the system can run this model (for local models).
    """

    id: str
    name: str
    context_length: int = 4096
    pricing: Optional[dict] = None
    free_tier: bool = False
    is_free: bool = False
    daily_limit: Optional[int] = None
    requires_payment: bool = False
    model_group_id: Optional[str] = None
    balance: Optional[float] = None
    limit_period: Optional[str] = None
    limit_tokens: Optional[int] = None
    downloaded: bool = False
    can_run: bool = True
