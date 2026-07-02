"""Database connection manager.

Provides a centralized async context manager for SQLite connections
so repositories don't each open their own connections.
"""

import aiosqlite
from pathlib import Path

from app.paths import DB_PATH


class DatabaseConnection:
    """Async context manager for aiosqlite connections.

    Ensures the data directory exists and provides a consistent
    connection interface for all repositories.

    Usage:
        async with DatabaseConnection() as db:
            await db.execute("SELECT 1")
    """

    def __init__(self, db_path: Path = DB_PATH):
        """Initialize with database file path.

        Args:
            db_path: Path to SQLite database file.
        """
        self._db_path = db_path

    async def __aenter__(self) -> aiosqlite.Connection:
        """Open database connection.

        Returns:
            Active aiosqlite connection.
        """
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self._db_path)
        await self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close database connection."""
        await self._conn.close()


async def get_connection() -> aiosqlite.Connection:
    """Get a new database connection (caller must close it).

    Returns:
        Active aiosqlite connection.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(DB_PATH)
    await conn.execute("PRAGMA foreign_keys = ON")
    return conn
