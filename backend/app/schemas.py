"""Pydantic request and response schemas used across the API.

Defines data models for chat messages, provider settings, health checks
and prompt compliance tests.
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union
from app.providers.config import PROVIDERS


class ContentImageUrl(BaseModel):
    """URL reference for an image included in message content."""
    url: str


class ContentPart(BaseModel):
    """A single part of a multi-modal message (text or image)."""
    type: Literal["text", "image_url"]
    text: Optional[str] = None
    image_url: Optional[ContentImageUrl] = None


class ChatMessage(BaseModel):
    """One message in a conversation with role and content."""
    role: Literal["user", "assistant", "system"]
    content: Union[str, List[ContentPart]]


class ChatRequest(BaseModel):
    """Payload for a streaming chat completion request.

    Attributes:
        messages: Conversation history.
        temperature: Sampling temperature (0.0–2.0).
        max_tokens: Maximum tokens to generate (64–32768).
        top_p: Nucleus sampling parameter (0.0–1.0).
        system_prompt: Optional system-level instruction.
        use_context: Whether to send full history or only the last user message.
    """
    messages: List[ChatMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=64, le=32768)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    system_prompt: Optional[str] = None
    use_context: bool = True


class HealthResponse(BaseModel):
    """Provider health status returned by the health endpoint."""
    status: str
    provider: str
    model: Optional[str] = None
    mock_mode: bool


class PromptTestResponse(BaseModel):
    """Result of the system-prompt compliance test."""
    follows_instructions: bool
    model_answer: str


class SettingsPayload(BaseModel):
    """Payload for configuring or updating the active LLM provider.

    Attributes:
        provider: Provider identifier.
        api_key: API key for authentication.
        model: Model name override.
        base_url: Optional custom API base URL.
    """
    provider: Literal[tuple(PROVIDERS)]
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None


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
    """
    id: str
    name: str
    context_length: int = 4096
    pricing: Optional[dict] = None
    free_tier: bool = False
