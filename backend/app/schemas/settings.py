"""Settings-related Pydantic schemas.

Defines request/response models for provider configuration endpoints.
"""

from pydantic import BaseModel
from typing import Literal, Optional

from app.providers.config import PROVIDERS


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
