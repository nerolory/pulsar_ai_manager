from typing import Optional
from app.providers.base import BaseLLMProvider

_provider: Optional[BaseLLMProvider] = None


def set_provider(provider: BaseLLMProvider) -> None:
    global _provider
    _provider = provider


def get_provider() -> Optional[BaseLLMProvider]:
    return _provider
