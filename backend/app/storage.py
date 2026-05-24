import yaml
from pathlib import Path
from typing import Optional
from loguru import logger

SETTINGS_FILE = Path("/app/data/settings.yaml")


def save_provider_config(provider: str, api_key: Optional[str], model: Optional[str], base_url: Optional[str]) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    config = {
        "provider": provider,
        "api_key": api_key,
        "model": model,
        "base_url": base_url,
    }
    with open(SETTINGS_FILE, "w") as f:
        yaml.dump(config, f)
    logger.info(f"Provider config saved: {provider}")


def load_provider_config() -> Optional[dict]:
    if not SETTINGS_FILE.exists():
        return None
    try:
        with open(SETTINGS_FILE) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load provider config: {e}")
        return None
