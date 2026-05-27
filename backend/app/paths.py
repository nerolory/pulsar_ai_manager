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
