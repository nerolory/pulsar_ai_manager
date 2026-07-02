"""Shared pytest fixtures."""

import pytest

DB_PATH_MODULES = (
    "app.paths",
    "app.database",
    "app.repositories.connection",
    "app.repositories.chat_repository",
    "app.repositories.message_repository",
    "app.repositories.model_cache_repository",
)


@pytest.fixture
def patch_db_path(monkeypatch, tmp_path):
    """Point all repository/database modules at an isolated SQLite file."""
    db_path = tmp_path / "test.db"
    for module in DB_PATH_MODULES:
        monkeypatch.setattr(f"{module}.DB_PATH", db_path)
    return db_path
