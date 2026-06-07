"""Provider factory with auto-registration.

Implements the Factory pattern with a class-level registry.
Each provider registers itself via the @register_provider decorator.
This eliminates the giant if/elif chain in routes/settings.py.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from app.providers.base import BaseLLMProvider


class ProviderConfig:
    """Typed configuration for provider initialization.

    Attributes:
        provider: Provider identifier string.
        api_key: API key for authentication.
        model: Model name/id to use.
        base_url: Optional custom API base URL.
    """

    def __init__(
        self,
        provider: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = base_url


class ProviderFactory:
    """Factory for creating LLM provider instances.

    Maintains a registry of provider classes. Providers register
    themselves using the @register_provider decorator.

    Usage:
        provider = ProviderFactory.create(ProviderConfig(
            provider="openrouter",
            api_key="sk-...",
            model="qwen/qwen3-235b-a22b:free",
        ))
    """

    _registry: dict[str, type[BaseLLMProvider]] = {}
    _default_models: dict[str, str] = {}
    _requires_api_key: dict[str, bool] = {}

    @classmethod
    def register(
        cls,
        name: str,
        default_model: str = "",
        requires_api_key: bool = True,
    ):
        """Decorator to register a provider class.

        Args:
            name: Provider identifier (e.g., "openrouter", "groq").
            default_model: Default model if none specified.
            requires_api_key: Whether API key is mandatory.

        Returns:
            Decorator function that registers the class.
        """

        def decorator(provider_cls: type[BaseLLMProvider]):
            cls._registry[name] = provider_cls
            cls._default_models[name] = default_model
            cls._requires_api_key[name] = requires_api_key
            return provider_cls

        return decorator

    @classmethod
    def create(cls, config: ProviderConfig) -> BaseLLMProvider:
        """Create a provider instance from configuration.

        Args:
            config: Provider configuration with credentials.

        Returns:
            Initialized provider instance.

        Raises:
            ValueError: If provider is unknown or API key is missing.
        """
        name = config.provider

        if name not in cls._registry:
            raise ValueError(f"Unknown provider: {name}. Available: {list(cls._registry.keys())}")

        if cls._requires_api_key.get(name, True) and not config.api_key:
            raise ValueError(f"api_key required for {name}")

        provider_cls = cls._registry[name]
        model = config.model or cls._default_models.get(name, "")

        # Build kwargs based on provider constructor
        kwargs = {"model": model}
        if config.api_key:
            kwargs["api_key"] = config.api_key
        if config.base_url:
            kwargs["base_url"] = config.base_url

        instance = provider_cls(**kwargs)
        logger.info(f"Provider created: {name} (model={model})")
        return instance

    @classmethod
    def get_registered(cls) -> list[str]:
        """Return list of all registered provider names.

        Returns:
            List of provider identifier strings.
        """
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a provider is registered.

        Args:
            name: Provider identifier.

        Returns:
            True if provider is in the registry.
        """
        return name in cls._registry
