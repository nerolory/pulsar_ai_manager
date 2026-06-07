import os
import sys
import uvicorn
from app.configs import settings

if __name__ == "__main__":
    is_frozen = getattr(sys, 'frozen', False)
    reload = not is_frozen and os.getenv("RELOAD", "true").lower() == "true"

    if is_frozen:
        from app.main import app
        uvicorn.run(app, host=settings.app_host, port=settings.app_port, reload=False)
    else:
        uvicorn.run(
            "app.main:app",
            host=settings.app_host,
            port=settings.app_port,
            reload=reload,
        )
