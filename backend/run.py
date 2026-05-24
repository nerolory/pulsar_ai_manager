import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    reload = os.getenv("RELOAD", "true").lower() == "true"
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=reload,
    )
