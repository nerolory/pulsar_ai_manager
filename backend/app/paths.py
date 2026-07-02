import os
import sys
from pathlib import Path


def _resolve_data_dir() -> Path:
    """Resolve persistent data directory for DB, settings and uploads.

    Priority:
    1. PyInstaller frozen executable — ./data next to the binary
    2. Docker — /app/data (volume mount)
    3. Local dev — backend/data/
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "data"

    if Path("/app/data").exists() or Path("/.dockerenv").exists():
        return Path("/app/data")

    env_override = os.getenv("PULSAR_DATA_DIR")
    if env_override:
        return Path(env_override)

    # backend/app/paths.py → backend/data
    return Path(__file__).resolve().parent.parent / "data"


DATA_DIR = _resolve_data_dir()
DB_PATH = DATA_DIR / "chats.db"
SETTINGS_FILE = DATA_DIR / "settings.yaml"
UPLOADS_DIR = DATA_DIR / "uploads"
BASE_DIR = Path(__file__).parent.parent.parent
# In Docker dev mode with volume mount, migrations are in /app/app/migrations
# In Docker prod or local dev, they might be in /app/migrations or backend/app/migrations
if (Path("/app/app/migrations")).exists():
    MIGRATIONS_DIR = Path("/app/app/migrations")
elif (BASE_DIR / "backend" / "app" / "migrations").exists():
    MIGRATIONS_DIR = BASE_DIR / "backend" / "app" / "migrations"
elif (Path("/app/migrations")).exists():
    MIGRATIONS_DIR = Path("/app/migrations")
else:
    MIGRATIONS_DIR = BASE_DIR / "backend" / "app" / "migrations"
