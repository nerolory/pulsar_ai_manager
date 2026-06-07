"""Pydantic schemas package — re-exports all schemas for backward compatibility.

New code should import from specific submodules:
    from app.schemas.chat import ChatMessage, ChatRequest
    from app.schemas.provider import ProviderCapabilities, ModelInfo
    from app.schemas.settings import SettingsPayload
"""

from app.schemas.chat import ContentImageUrl, ContentPart, ChatMessage, ChatRequest  # noqa: F401
from app.schemas.provider import ProviderCapabilities, ModelInfo  # noqa: F401
from app.schemas.settings import SettingsPayload, HealthResponse, PromptTestResponse  # noqa: F401
