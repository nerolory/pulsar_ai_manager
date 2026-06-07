"""Storage service — typed class for managing YAML-based settings.

Wraps the raw YAML I/O from storage.py in a proper class with
typed methods and clear responsibility.
"""

from typing import Optional

import yaml
from loguru import logger

from app.paths import SETTINGS_FILE


class StorageService:
    """Manages persistent provider settings in a YAML file.

    Provides typed read/write access to provider configurations
    stored in settings.yaml.

    Attributes:
        settings_file: Path to the YAML settings file.
    """

    def __init__(self):
        """Initialize with the default settings file path."""
        self.settings_file = SETTINGS_FILE

    def _load_yaml(self) -> dict:
        """Load and parse the YAML settings file.

        Returns:
            Parsed dict or empty dict on failure.
        """
        if not self.settings_file.exists():
            return {}
        try:
            with open(self.settings_file) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return {}

    def _save_yaml(self, data: dict) -> None:
        """Write data back to the YAML settings file.

        Args:
            data: Dict to serialize to YAML.
        """
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.settings_file, "w") as f:
            yaml.dump(data, f)

    def save_provider_config(
        self,
        provider: str,
        api_key: Optional[str],
        model: Optional[str],
        base_url: Optional[str],
    ) -> None:
        """Save provider configuration to settings.

        Args:
            provider: Provider identifier.
            api_key: API key for the provider.
            model: Model identifier.
            base_url: Optional custom base URL.
        """
        data = self._load_yaml()
        data["active_provider"] = provider
        data[provider] = {
            "api_key": api_key,
            "model": model,
            "base_url": base_url,
        }
        self._save_yaml(data)
        logger.info(f"Provider config saved: {provider}")

    def load_provider_config(self) -> Optional[dict]:
        """Load the active provider configuration.

        Returns:
            Dict with provider, api_key, model, base_url or None if not configured.
        """
        data = self._load_yaml()
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

    def load_provider_config_for(self, provider: str) -> Optional[dict]:
        """Load configuration for a specific provider.

        Args:
            provider: Provider identifier to look up.

        Returns:
            Dict with api_key, model, base_url or None if not found.
        """
        data = self._load_yaml()
        config = data.get(provider)
        if not config:
            return None
        return {
            "provider": provider,
            "api_key": config.get("api_key"),
            "model": config.get("model"),
            "base_url": config.get("base_url"),
        }

    def get_all_provider_configs(self) -> dict:
        """Get all saved provider configs (for the frontend settings page).

        Returns:
            Dict mapping provider names to their saved configs.
        """
        from app.providers.config import PROVIDERS

        data = self._load_yaml()
        return {
            provider_name: {
                "api_key": data[provider_name].get("api_key"),
                "model": data[provider_name].get("model"),
            }
            for provider_name in PROVIDERS
            if provider_name in data
        }
