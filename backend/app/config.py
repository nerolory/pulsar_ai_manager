"""Application configuration loaded from environment variables.

Uses Pydantic Settings to read values from the optional .env file
and provides typed access to host, port, CORS and feature flags.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union


class Settings(BaseSettings):
    """Typed application settings with environment overrides."""
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_enabled: bool = True
    mock_mode: bool = False
    electron_mode: bool = False
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Split the CORS origins string into a list.

        Returns:
            List[str]: Individual origin strings, or ["*"] in electron mode.
        """
        if self.electron_mode:
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
