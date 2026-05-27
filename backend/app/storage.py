import yaml
from pathlib import Path
from typing import Optional
from loguru import logger

from app.paths import SETTINGS_FILE


def _load_yaml() -> dict:
    if not SETTINGS_FILE.exists():
        return {}
    try:
        with open(SETTINGS_FILE) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        return {}


def save_provider_config(provider: str, api_key: Optional[str], model: Optional[str], base_url: Optional[str]) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = _load_yaml()
    data["active_provider"] = provider
    data[provider] = {
        "api_key": api_key,
        "model": model,
        "base_url": base_url,
    }
    with open(SETTINGS_FILE, "w") as f:
        yaml.dump(data, f)
    logger.info(f"Provider config saved: {provider}")


def load_provider_config() -> Optional[dict]:
    data = _load_yaml()
    active = data.get("active_provider")
    if not active:
        return None
    config = data.get(active, {})
    return {
        "provider": active,
        "api_key": config.get("api_key"),
        "model": config.get("model"),
        "base_url": config.get("base_url"),
    }


def load_provider_config_for(provider: str) -> Optional[dict]:
    data = _load_yaml()
    config = data.get(provider)
    if not config:
        return None
    return {
        "provider": provider,
        "api_key": config.get("api_key"),
        "model": config.get("model"),
        "base_url": config.get("base_url"),
    }
