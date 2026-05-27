"""PulsarAI FastAPI application entrypoint.

Initialises the database, restores the active LLM provider on startup,
configures CORS and mounts all API routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.config import settings
from app.routes.chat import router as chat_router
from app.routes.settings import router as settings_router
from app.routes.chats import router as chats_router
from app.routes.uploads import router as uploads_router
from app.state import set_provider

# ── Logging ────────────────────────────────────────
if not settings.log_enabled:
    logger.disable("app")
else:
    logger.remove()
    logger.add(sys.stderr, level="INFO", colorize=True,
               format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


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
        from app.providers.mock import MockProvider
        set_provider(MockProvider())
        logger.info("MockProvider activated (MOCK_MODE=true)")
    else:
        from app.storage import load_provider_config
        from app.routes.settings import init_provider
        config = load_provider_config()
        if config and config.get("provider"):
            try:
                init_provider(config["provider"], config.get("api_key"), config.get("model"), config.get("base_url"))
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

app.include_router(chat_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(chats_router, prefix="/api/v1")
app.include_router(uploads_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Return basic application metadata.

    Returns:
        dict: App name, version and docs URL.
    """
    return {"app": "PulsarAI", "version": "0.1.0", "docs": "/docs"}
