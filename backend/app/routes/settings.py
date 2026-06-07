"""Settings routes for LLM provider configuration and health monitoring.

Provides endpoints for configuring providers, retrieving saved configurations,
running prompt compliance tests, and checking provider health status.
"""

from fastapi import APIRouter, HTTPException
from app.schemas import SettingsPayload, HealthResponse, PromptTestResponse
from app.state import set_provider, get_provider
from app.config import settings
from app.storage import save_provider_config
from loguru import logger

router = APIRouter(prefix="/settings", tags=["settings"])


def init_provider(provider: str, api_key: str | None, model: str | None, base_url: str | None) -> None:
    """Initialize the active LLM provider with the given credentials.

    Args:
        provider: Provider identifier ("openrouter", "vsellm", "anthropic", "groq", "cerebras", "qwen", "mistral", "gemini", "mock").
        api_key: API key for the selected provider.
        model: Model name to use.
        base_url: Optional custom base URL.

    Raises:
        ValueError: If the provider is unknown or the API key is missing.
    """
    if provider == "mock" or settings.mock_mode:
        from app.providers.mock import MockProvider
        set_provider(MockProvider())
    elif provider == "openrouter":
        if not api_key:
            raise ValueError("api_key required for OpenRouter")
        from app.providers.openrouter import OpenRouterProvider
        set_provider(OpenRouterProvider(
            api_key=api_key,
            model=model or "qwen/qwen3-235b-a22b:free",
        ))
    elif provider == "vsellm":
        if not api_key:
            raise ValueError("api_key required for VseLLM")
        from app.providers.vsellm import VseLLMProvider
        set_provider(VseLLMProvider(
            api_key=api_key,
            model=model or "openai/gpt-4o-mini",
        ))
    elif provider == "anthropic":
        if not api_key:
            raise ValueError("api_key required for Anthropic")
        from app.providers.anthropic import AnthropicProvider
        set_provider(AnthropicProvider(
            api_key=api_key,
            model=model or "claude-3-5-sonnet-20241022",
        ))
    elif provider == "groq":
        if not api_key:
            raise ValueError("api_key required for Groq")
        from app.providers.groq import GroqProvider
        set_provider(GroqProvider(
            api_key=api_key,
            model=model or "llama-3.1-70b-versatile",
        ))
    elif provider == "cerebras":
        if not api_key:
            raise ValueError("api_key required for Cerebras")
        from app.providers.cerebras import CerebrasProvider
        set_provider(CerebrasProvider(
            api_key=api_key,
            model=model or "llama3.1-70b",
        ))
    elif provider == "qwen":
        if not api_key:
            raise ValueError("api_key required for Qwen")
        from app.providers.qwen import QwenProvider
        set_provider(QwenProvider(
            api_key=api_key,
            model=model or "qwen-max",
        ))
    elif provider == "mistral":
        if not api_key:
            raise ValueError("api_key required for Mistral")
        from app.providers.mistral import MistralProvider
        set_provider(MistralProvider(
            api_key=api_key,
            model=model or "mistral-large-latest",
        ))
    elif provider == "gemini":
        if not api_key:
            raise ValueError("api_key required for Gemini")
        from app.providers.gemini import GeminiProvider
        set_provider(GeminiProvider(
            api_key=api_key,
            model=model or "gemini-2.0-flash-exp",
        ))
    else:
        raise ValueError(f"Unknown provider: {provider}")
    logger.info(f"Provider set to: {provider}")


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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/provider")
async def get_provider_config():
    """Return the active provider configuration and all saved provider configs.

    Returns:
        dict: Active provider details plus a map of all previously saved providers.
    """
    from app.storage import load_provider_config, load_provider_config_for, _load_yaml
    config = load_provider_config()
    data = _load_yaml()
    known_providers = ["openrouter", "vsellm", "openai", "mock"]
    all_providers = {
        provider_name: {"api_key": data[provider_name].get("api_key"), "model": data[provider_name].get("model")}
        for provider_name in known_providers if provider_name in data
    }
    if not config:
        return {"provider": None, "model": None, "api_key": None, "all_providers": all_providers}
    return {
        "provider": config.get("provider"),
        "model": config.get("model"),
        "api_key": config.get("api_key"),
        "all_providers": all_providers,
    }


_TEST_SYSTEM = "Respond with exactly one word: YES. Nothing else."
_TEST_USER   = "Are you able to follow instructions?"
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
        max_tokens=16,
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
        raise HTTPException(status_code=500, detail=str(e))


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
