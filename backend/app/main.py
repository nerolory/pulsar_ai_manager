"""PulsarAI FastAPI application entrypoint.

Initialises the database, restores the active LLM provider on startup,
configures CORS and mounts all API routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.configs import settings
from app.routes.chat import router as chat_router
from app.routes.settings import router as settings_router
from app.routes.chats import router as chats_router
from app.routes.uploads import router as uploads_router
from app.routes.admin import router as admin_router
from app.routes.voice import router as voice_router
from app.state import set_provider
from app.exceptions import (
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    BalanceError,
    NetworkError,
    ProviderUnavailableError,
    InvalidRequestError,
)

# ── Logging ────────────────────────────────────────
if not settings.log_enabled:
    logger.disable("app")
else:
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
    )


# ── App ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan: initialise DB and restore the saved provider.

    Args:
        application: The FastAPI app instance.

    Yields:
        None: Control passes to the running application.
    """
    from app.database import init_db

    await init_db()

    if settings.mock_mode:
        from app.providers.factory import ProviderFactory, ProviderConfig
        import app.providers

        app.providers.register_all()
        mock_instance = ProviderFactory.create(ProviderConfig(provider="mock"))
        set_provider(mock_instance)
        logger.info("MockProvider activated (MOCK_MODE=true)")
    else:
        from app.storage import load_provider_config
        from app.routes.settings import init_provider

        config = load_provider_config()
        if config and config.get("provider"):
            try:
                init_provider(
                    config["provider"],
                    config.get("api_key"),
                    config.get("model"),
                    config.get("base_url"),
                )
                logger.info(f"Provider restored from settings.yaml: {config['provider']}")
            except Exception as e:
                logger.error(f"Failed to restore provider: {e}")
        else:
            logger.info("No provider set — configure via POST /api/v1/settings/provider")

    yield


app = FastAPI(title="PulsarAI Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ─────────────────────────────────
@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors."""
    logger.error(f"Authentication error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=401,
        content={"error": "Ошибка аутентификации", "message": exc.message},
    )


@app.exception_handler(RateLimitError)
async def rate_limit_error_handler(request: Request, exc: RateLimitError):
    """Handle rate limit errors."""
    logger.error(f"Rate limit error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=429,
        content={"error": "Превышен лимит запросов", "message": exc.message},
    )


@app.exception_handler(ModelNotFoundError)
async def model_not_found_error_handler(request: Request, exc: ModelNotFoundError):
    """Handle model not found errors."""
    logger.error(f"Model not found error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=404,
        content={"error": "Модель не найдена", "message": exc.message},
    )


@app.exception_handler(BalanceError)
async def balance_error_handler(request: Request, exc: BalanceError):
    """Handle balance errors."""
    logger.error(f"Balance error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=402,
        content={"error": "Недостаточно средств", "message": exc.message},
    )


@app.exception_handler(NetworkError)
async def network_error_handler(request: Request, exc: NetworkError):
    """Handle network errors."""
    logger.error(f"Network error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={"error": "Ошибка сети", "message": exc.message},
    )


@app.exception_handler(ProviderUnavailableError)
async def provider_unavailable_error_handler(request: Request, exc: ProviderUnavailableError):
    """Handle provider unavailable errors."""
    logger.error(f"Provider unavailable error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={"error": "Провайдер недоступен", "message": exc.message},
    )


@app.exception_handler(InvalidRequestError)
async def invalid_request_error_handler(request: Request, exc: InvalidRequestError):
    """Handle invalid request errors."""
    logger.error(f"Invalid request error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content={"error": "Неверный запрос", "message": exc.message},
    )


@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError):
    """Handle generic provider errors."""
    logger.error(f"Provider error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Ошибка провайдера", "message": exc.message},
    )


app.include_router(chat_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(chats_router, prefix="/api/v1")
app.include_router(uploads_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(voice_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Return basic application metadata.

    Returns:
        dict: App name, version and docs URL.
    """
    return {"app": "PulsarAI", "version": "0.1.0", "docs": "/docs"}
