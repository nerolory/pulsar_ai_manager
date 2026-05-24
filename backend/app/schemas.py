from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=64, le=32768)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    system_prompt: Optional[str] = None
    use_context: bool = True


class HealthResponse(BaseModel):
    status: str
    provider: str
    model: Optional[str] = None
    mock_mode: bool


class PromptTestResponse(BaseModel):
    follows_instructions: bool
    model_answer: str


class SettingsPayload(BaseModel):
    provider: Literal["openrouter", "vsellm", "openai", "gigachat", "mock"]
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
