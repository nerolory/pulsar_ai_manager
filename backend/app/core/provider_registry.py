"""Provider registry — manages the active LLM provider instance.

Replaces the global mutable variable pattern with a proper singleton class.
Backward-compatible: still exports set_provider/get_provider functions.
"""

from typing import Optional

from app.providers.base import BaseLLMProvider


class ProviderRegistry:
    """Singleton registry for the currently active LLM provider.

    Provides thread-safe access to the active provider instance
    with clear set/get semantics.
    """

    _instance: Optional["ProviderRegistry"] = None
    _provider: Optional[BaseLLMProvider] = None

    def __new__(cls):
        """Ensure only one instance exists (singleton)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def provider(self) -> Optional[BaseLLMProvider]:
        """Get the currently active provider.

        Returns:
            The active BaseLLMProvider instance or None.
        """
        return self._provider

    @provider.setter
    def provider(self, value: Optional[BaseLLMProvider]):
        """Set the active provider.

        Args:
            value: Provider instance or None to clear.
        """
        self._provider = value


# Backward-compatible module-level functions
_registry = ProviderRegistry()


def set_provider(provider: Optional[BaseLLMProvider]) -> None:
    """Set the active LLM provider (backward-compatible wrapper).

    Args:
        provider: Provider instance to activate.
    """
    _registry.provider = provider


def get_provider() -> Optional[BaseLLMProvider]:
    """Get the active LLM provider (backward-compatible wrapper).

    Returns:
        The active BaseLLMProvider instance or None.
    """
    return _registry.provider
