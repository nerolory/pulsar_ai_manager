from abc import ABC, abstractmethod
from typing import AsyncIterator
from app.schemas import ChatRequest, ChatMessage


class BaseLLMProvider(ABC):
    """Abstract base for all LLM providers."""

    model: str = "unknown"

    @abstractmethod
    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        """Stream chat completion tokens."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if provider is reachable."""
        ...
