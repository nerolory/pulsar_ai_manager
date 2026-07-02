"""Settings routes for LLM provider configuration and health monitoring.

Provides endpoints for configuring providers, retrieving saved configurations,
running prompt compliance tests, and checking provider health status.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas import (
    SettingsPayload,
    HealthResponse,
    PromptTestResponse,
    ProviderCapabilities,
    ModelInfo,
)
from app.state import set_provider, get_provider
from app.configs import settings
from app.storage import save_provider_config
from app.repositories.model_cache_repository import ModelCacheRepository
from app.providers.config import (
    PROVIDERS,
    PROVIDER_METADATA,
    BASE_URL_TO_PROVIDER,
    OPENAI_COMPATIBLE_PROVIDERS,
    PROVIDER_MODEL_NAMES,
)
from app.configs.free_models import is_model_free, get_model_group, MODEL_GROUPS
from loguru import logger

router = APIRouter(prefix="/settings", tags=["settings"])


class DetectProviderRequest(BaseModel):
    """Payload for provider auto-detection from base URL."""

    base_url: str


class SwitchModelRequest(BaseModel):
    """Payload for switching the active model."""

    model: str


def _mask_api_key(api_key: str | None) -> str | None:
    """Return a masked API key safe for client responses."""
    if not api_key:
        return None
    if len(api_key) <= 8:
        return "***"
    return f"{api_key[:4]}...{api_key[-4:]}"


def _mask_provider_entry(entry: dict) -> dict:
    """Mask api_key inside a provider config dict."""
    masked = dict(entry)
    if "api_key" in masked:
        masked["api_key"] = _mask_api_key(masked.get("api_key"))
    return masked


def init_provider(
    provider: str, api_key: str | None, model: str | None, base_url: str | None
) -> None:
    """Initialize the active LLM provider with the given credentials.

    Uses ProviderFactory to create the appropriate provider instance
    based on the registered providers.

    Args:
        provider: Provider identifier (e.g., "openrouter", "vsellm", "mock").
        api_key: API key for the selected provider.
        model: Model name to use.
        base_url: Optional custom base URL.

    Raises:
        ValueError: If the provider is unknown or the API key is missing.
    """
    from app.providers.factory import ProviderFactory, ProviderConfig
    import app.providers

    app.providers.register_all()

    if settings.mock_mode:
        provider = "mock"

    config = ProviderConfig(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
    )
    instance = ProviderFactory.create(config)
    set_provider(instance)


async def _fetch_local_llm_models(free: bool = False) -> list[dict]:
    """List downloaded local models without requiring an active remote provider."""
    import app.providers
    from app.providers.factory import ProviderFactory, ProviderConfig

    app.providers.register_all()
    default_model = ProviderFactory._default_models.get("local_llm", "phi-3-mini-3.8b")
    instance = ProviderFactory.create(ProviderConfig(provider="local_llm", model=default_model))
    models = await instance.list_models()
    models_dict = [model.model_dump() for model in models]
    for model in models_dict:
        model["is_free"] = True
    if free:
        models_dict = [m for m in models_dict if m.get("is_free", False)]
    return models_dict


@router.post("/provider")
async def configure_provider(payload: SettingsPayload):
    """Configure and save the active LLM provider.

    Args:
        payload: SettingsPayload containing provider, api_key, model and base_url.

    Returns:
        dict: Status confirmation with the active provider name.

    Raises:
        HTTPException: On validation or internal errors.
    """
    try:
        from app.storage import load_provider_config_for

        api_key = payload.api_key
        if not api_key:
            saved = load_provider_config_for(payload.provider)
            if saved:
                api_key = saved.get("api_key")
        init_provider(payload.provider, api_key, payload.model, payload.base_url)
        save_provider_config(payload.provider, api_key, payload.model, payload.base_url)
        return {"status": "ok", "provider": payload.provider}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to configure provider: {e}")
        raise HTTPException(status_code=500, detail="Failed to configure provider")


@router.get("/provider")
async def get_provider_config():
    """Return the active provider configuration and all saved provider configs.

    Returns:
        dict: Active provider details plus a map of all previously saved providers.
    """
    from app.storage import load_provider_config, load_provider_config_for, _load_yaml

    config = load_provider_config()
    data = _load_yaml()
    all_providers = {
        provider_name: _mask_provider_entry(
            {
                "api_key": data[provider_name].get("api_key"),
                "model": data[provider_name].get("model"),
            }
        )
        for provider_name in PROVIDERS
        if provider_name in data
    }
    if not config:
        return {"provider": None, "model": None, "api_key": None, "all_providers": all_providers}
    return {
        "provider": config.get("provider"),
        "model": config.get("model"),
        "api_key": _mask_api_key(config.get("api_key")),
        "all_providers": all_providers,
    }


@router.get("/providers")
async def get_providers_list():
    """Return list of all available providers with metadata.

    Returns:
        dict: Provider metadata for frontend.
    """
    # Add model_name to each provider's metadata
    providers_with_model_name = {}
    for provider_id, metadata in PROVIDER_METADATA.items():
        providers_with_model_name[provider_id] = {
            **metadata,
            "model_name": PROVIDER_MODEL_NAMES.get(provider_id, "model_default"),
        }
    return {"providers": providers_with_model_name}


@router.post("/detect-provider")
async def detect_provider(request: DetectProviderRequest):
    """Detect provider from base URL.

    Args:
        request: Request body with base_url to check.

    Returns:
        dict: Detected provider ID and compatibility info.
    """
    from urllib.parse import urlparse

    base_url = request.base_url
    parsed = urlparse(base_url)
    domain = parsed.netloc

    # Check if domain matches known provider
    for pattern, provider_id in BASE_URL_TO_PROVIDER.items():
        if pattern in domain:
            return {
                "provider": provider_id,
                "detected": True,
                "compatible": True,
            }

    # Check if it's OpenAI-compatible (custom endpoint)
    return {
        "provider": None,
        "detected": False,
        "compatible": True,  # Assume OpenAI-compatible for custom endpoints
        "message_code": "provider_openai_compatible",
    }


_TEST_SYSTEM = "Respond with exactly one word: YES. Nothing else."
_TEST_USER = "Are you able to follow instructions?"
_TEST_MARKER = "YES"


@router.post("/test-prompt", response_model=PromptTestResponse)
async def test_prompt():
    """Send a system-prompt compliance test to the active provider.

    Returns:
        PromptTestResponse: Whether the model followed the instruction and its answer.

    Raises:
        HTTPException: If no provider is configured or the test fails.
    """
    provider = get_provider()
    if provider is None:
        raise HTTPException(status_code=503, detail="No provider configured")

    from app.schemas import ChatRequest, ChatMessage

    request = ChatRequest(
        messages=[
            ChatMessage(role="system", content=_TEST_SYSTEM),
            ChatMessage(role="user", content=_TEST_USER),
        ],
        temperature=0.0,
        max_tokens=64,
    )
    try:
        chunks = []
        async for token in provider.chat(request):
            chunks.append(token)
            if len(chunks) > 50:
                break
        answer = "".join(chunks).strip()
        follows = _TEST_MARKER.lower() in answer.lower()
        logger.info(f"Prompt test result: '{answer}' → follows={follows}")
        return PromptTestResponse(follows_instructions=follows, model_answer=answer)
    except Exception as e:
        logger.error(f"Prompt test failed: {e}")
        raise HTTPException(status_code=500, detail="Prompt test failed")


@router.get("/health", response_model=HealthResponse)
async def health():
    """Check the health status of the currently active LLM provider.

    Returns:
        HealthResponse: Status, provider name, model and mock mode flag.
    """
    provider = get_provider()
    if provider is None:
        return HealthResponse(status="no_provider", provider="none", mock_mode=settings.mock_mode)

    ok = await provider.health_check()
    return HealthResponse(
        status="ok" if ok else "error",
        provider=provider.model or type(provider).__name__,
        model=provider.model,
        mock_mode=settings.mock_mode,
    )


@router.get("/capabilities", response_model=ProviderCapabilities)
async def get_capabilities():
    """Get capabilities of the currently active LLM provider.

    Returns:
        ProviderCapabilities: Capabilities of the current provider.

    Raises:
        HTTPException: If no provider is configured.
    """
    provider = get_provider()
    if provider is None:
        raise HTTPException(status_code=503, detail="No provider configured")

    return provider.get_capabilities()


@router.get("/models")
async def get_models(refresh: bool = False, provider: str = None, free: bool = False):
    """Get list of available models for the current or specified provider.

    Args:
        refresh: Force refresh from API instead of using cache.
        provider: Optional provider ID to get models for (instead of active provider).
        free: Filter to only return free models.

    Returns:
        dict: List of models with metadata.

    Raises:
        HTTPException: If no provider is configured or fetching fails.
    """
    if provider == "local_llm":
        cached = await ModelCacheRepository.get("local_llm")
        if cached and not refresh:
            models = cached
            if free:
                models = [m for m in models if m.get("is_free", False)]
            return {"models": models, "source": "cache"}
        try:
            models_dict = await _fetch_local_llm_models(free=free)
            await ModelCacheRepository.cache("local_llm", models_dict)
            return {"models": models_dict, "source": "local"}
        except Exception as e:
            logger.error(f"Failed to list local LLM models: {e}")
            raise HTTPException(status_code=500, detail="Failed to list local models")

    if provider:
        # For non-active providers, try cache first
        cached = await ModelCacheRepository.get(provider)
        if cached and not refresh:
            models = cached
            if free:
                models = [m for m in models if m.get("is_free", False)]
            return {"models": models, "source": "cache"}
        # If refresh forced or no cache, try to get provider instance and fetch from API
        provider_instance = get_provider()
        if provider_instance is None:
            # Can't fetch without active provider, return cache if available
            if cached:
                models = cached
                if free:
                    models = [m for m in models if m.get("is_free", False)]
                return {"models": models, "source": "cache"}
            return {
                "models": [],
                "source": "cache",
                "message": "No cached models available. Please activate this provider first.",
            }
        # Provider is active, fetch from API
        from app.storage import load_provider_config

        active_config = load_provider_config() or {}
        active_provider_id = active_config.get("provider", "")
        provider_name = provider
        if active_provider_id != provider:
            # Requested provider is not the active one, return cache if available
            if cached:
                models = cached
                if free:
                    models = [m for m in models if m.get("is_free", False)]
                return {"models": models, "source": "cache"}
            # If no cache and provider is not active, try to initialize it temporarily
            # This allows fetching models for vsellm without activating it
            from app.storage import load_provider_config

            config = load_provider_config()
            if config and config.get("provider") == provider:
                # Temporarily initialize the provider to fetch models
                try:
                    init_provider(
                        provider, config.get("api_key"), config.get("model"), config.get("base_url")
                    )
                    temp_provider = get_provider()
                    if temp_provider:
                        models = await temp_provider.list_models()
                        await ModelCacheRepository.cache(provider, models)
                        if free:
                            models = [m for m in models if m.get("is_free", False)]
                        # Restore original provider
                        if config.get("provider"):
                            init_provider(
                                config.get("provider"),
                                config.get("api_key"),
                                config.get("model"),
                                config.get("base_url"),
                            )
                        return {"models": models, "source": "api"}
                except Exception as e:
                    logger.error(f"Failed to fetch models for provider {provider}: {e}")
                    return {
                        "models": [],
                        "source": "cache",
                        "message": f"Failed to fetch models: {str(e)}",
                    }
            return {
                "models": [],
                "source": "cache",
                "message": "No cached models available. Please activate this provider first.",
            }
    else:
        provider_instance = get_provider()
        if provider_instance is None:
            raise HTTPException(status_code=503, detail="No provider configured")
        from app.storage import load_provider_config

        active_config = load_provider_config() or {}
        provider_name = active_config.get("provider") or provider

    # Try cache first unless refresh is forced
    if not refresh:
        cached = await ModelCacheRepository.get(provider_name)
        if cached:
            models = cached
            if free:
                models = [m for m in models if m.get("is_free", False)]
            return {"models": models, "source": "cache"}

    # Fetch from provider
    try:
        models = await provider_instance.list_models()
        models_dict = [model.model_dump() for model in models]

        # Get provider balance if available
        balance_info = await provider_instance.check_balance()
        provider_balance = balance_info.get("balance") if balance_info else None

        # Add free model metadata and balance
        for model in models_dict:
            model_id = model.get("id", "")
            model["is_free"] = is_model_free(model_id)
            model["model_group_id"] = get_model_group(model_id)
            # Add provider balance to each model (for providers with balance API)
            if provider_balance is not None:
                model["balance"] = provider_balance

        # Filter by free if requested
        if free:
            models_dict = [m for m in models_dict if m.get("is_free", False)]

        # Cache the results
        await ModelCacheRepository.cache(provider_name, models_dict)

        return {"models": models_dict, "source": "api"}
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch models")


@router.get("/model-groups")
async def get_model_groups():
    """Get list of model groups for free/paid version grouping.

    Returns:
        dict: List of model groups with metadata.
    """
    return {"groups": MODEL_GROUPS}


@router.post("/switch-model")
async def switch_model(request: SwitchModelRequest):
    """Switch to a different model for the current provider.

    Args:
        request: JSON body with model ID to switch to.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If no provider is configured or switching fails.
    """
    model = request.model
    provider = get_provider()
    if provider is None:
        raise HTTPException(status_code=503, detail="No provider configured")

    try:
        # Update provider with new model
        provider.model = model
        # Save to storage
        from app.storage import load_provider_config

        config = load_provider_config()
        if config:
            save_provider_config(
                config["provider"], config.get("api_key"), model, config.get("base_url")
            )
        return {"success": True, "model": model}
    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        raise HTTPException(status_code=500, detail="Failed to switch model")


@router.post("/refresh-models")
async def refresh_models():
    """Force refresh the model list from the provider API.

    Returns:
        dict: List of models with metadata.

    Raises:
        HTTPException: If no provider is configured or fetching fails.
    """
    return await get_models(refresh=True)


@router.get("/balance")
async def get_balance():
    """Get account balance for the active provider.

    Returns:
        dict: Balance information or message if not supported.

    Raises:
        HTTPException: If no provider is configured.
    """
    provider = get_provider()
    if not provider:
        raise HTTPException(status_code=400, detail="No provider configured")

    logger.info(f"Checking balance for provider: {provider.__class__.__name__}")
    balance_info = await provider.check_balance()
    logger.info(f"Balance info: {balance_info}")
    if balance_info is None:
        return {"balance": None, "message_code": "balance_not_tracked"}
    return {"balance": balance_info}
