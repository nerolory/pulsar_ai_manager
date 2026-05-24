from fastapi import APIRouter, HTTPException
from app.schemas import SettingsPayload, HealthResponse, PromptTestResponse
from app.state import set_provider, get_provider
from app.config import settings
from app.storage import save_provider_config
from loguru import logger

router = APIRouter(prefix="/settings", tags=["settings"])


def init_provider(provider: str, api_key: str | None, model: str | None, base_url: str | None) -> None:
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
    else:
        raise ValueError(f"Unknown provider: {provider}")
    logger.info(f"Provider set to: {provider}")


@router.post("/provider")
async def configure_provider(payload: SettingsPayload):
    try:
        init_provider(payload.provider, payload.api_key, payload.model, payload.base_url)
        save_provider_config(payload.provider, payload.api_key, payload.model, payload.base_url)
        return {"status": "ok", "provider": payload.provider}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to configure provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/provider")
async def get_provider_config():
    from app.storage import load_provider_config
    config = load_provider_config()
    if not config:
        return {"provider": None, "model": None}
    return {
        "provider": config.get("provider"),
        "model": config.get("model"),
    }


_TEST_SYSTEM = "Respond with exactly one word: YES. Nothing else."
_TEST_USER   = "Are you able to follow instructions?"
_TEST_MARKER = "YES"


@router.post("/test-prompt", response_model=PromptTestResponse)
async def test_prompt():
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
