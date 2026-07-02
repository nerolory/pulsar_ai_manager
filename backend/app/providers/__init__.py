"""LLM Providers package.

This __init__.py is intentionally kept minimal to avoid circular imports.
Use `from app.providers.factory import ProviderFactory, ProviderConfig`
or call `app.providers.register_all()` to load all provider modules.
"""

# Provider module paths for lazy registration
_PROVIDER_MODULES = [
    "app.providers.openrouter",
    "app.providers.vsellm",
    "app.providers.openai_provider",
    "app.providers.anthropic",
    "app.providers.groq",
    "app.providers.cerebras",
    "app.providers.qwen",
    "app.providers.mistral",
    "app.providers.gemini",
    "app.providers.gigachat",
    "app.providers.mock",
    "app.providers.local_llm",
]

_registered = False


def register_all():
    """Import all provider modules to trigger @ProviderFactory.register decorators.

    Safe to call multiple times — only runs once.
    Providers with missing SDKs are silently skipped.
    """
    global _registered
    if _registered:
        return
    _registered = True

    import importlib
    from loguru import logger

    for module_path in _PROVIDER_MODULES:
        try:
            importlib.import_module(module_path)
        except ImportError as e:
            logger.debug(f"Skipping provider {module_path}: {e}")
        except Exception as e:
            logger.warning(f"Failed to load provider {module_path}: {e}")
