from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Optional
from app.schemas import ChatRequest, ChatMessage, ProviderCapabilities, ModelInfo


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

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Return provider capabilities."""
        ...

    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """Return list of available models."""
        ...

    async def check_balance(self) -> Optional[dict]:
        """Check account balance. Returns dict with balance info or None if not supported."""
        return None
