import sys
from pathlib import Path


def _resolve_data_dir() -> Path:
    if getattr(sys, 'frozen', False):
        # PyInstaller: data directory sits next to the compiled executable
        return Path(sys.executable).parent / 'data'
    # Docker / local dev
    return Path('/app/data')


DATA_DIR   = _resolve_data_dir()
DB_PATH    = DATA_DIR / 'chats.db'
SETTINGS_FILE = DATA_DIR / 'settings.yaml'
UPLOADS_DIR = DATA_DIR / 'uploads'
BASE_DIR   = Path(__file__).parent.parent.parent
# In Docker dev mode with volume mount, migrations are in /app/app/migrations
# In Docker prod or local dev, they might be in /app/migrations or backend/app/migrations
if (Path('/app/app/migrations')).exists():
    MIGRATIONS_DIR = Path('/app/app/migrations')
elif (BASE_DIR / 'backend' / 'app' / 'migrations').exists():
    MIGRATIONS_DIR = BASE_DIR / 'backend' / 'app' / 'migrations'
elif (Path('/app/migrations')).exists():
    MIGRATIONS_DIR = Path('/app/migrations')
else:
    MIGRATIONS_DIR = BASE_DIR / 'backend' / 'app' / 'migrations'
