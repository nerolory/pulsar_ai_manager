"""Global provider state management.

Holds a singleton reference to the currently active LLM provider
so it can be accessed from any route without passing it around.
"""

from typing import Optional
from app.providers.base import BaseLLMProvider

_provider: Optional[BaseLLMProvider] = None


def set_provider(provider: BaseLLMProvider) -> None:
    """Set the global active LLM provider.

    Args:
        provider: Initialised provider instance to use for all chat requests.
    """
    global _provider
    _provider = provider


def get_provider() -> Optional[BaseLLMProvider]:
    """Return the currently active LLM provider, if any.

    Returns:
        Optional[BaseLLMProvider]: The active provider or None.
    """
    return _provider
