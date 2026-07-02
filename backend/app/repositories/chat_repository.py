"""Chat repository — CRUD operations for chats table."""

from pathlib import Path
from typing import List, Optional
from datetime import datetime

import aiosqlite
from loguru import logger

from app.paths import DB_PATH


class ChatRepository:
    """Data access layer for the chats table.

    Provides methods for creating, reading, updating and deleting chats.
    Each method opens its own connection for simplicity with aiosqlite.
    """

    @staticmethod
    async def save(chat_id: str, title: str, db_path: Path = DB_PATH) -> None:
        """Upsert chat metadata (creates or updates title/timestamp).

        Args:
            chat_id: Unique chat identifier.
            title: Chat title to set.
            db_path: Optional custom database path for testing.
        """
        now = int(datetime.now().timestamp() * 1000)
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                """
                INSERT INTO chats (id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    updated_at = excluded.updated_at
            """,
                (chat_id, title, now, now),
            )
            await db.commit()
            logger.debug(f"Upserted chat {chat_id}")

    @staticmethod
    async def get_list(db_path: Path = DB_PATH) -> List[dict]:
        """Get all chats ordered by sort_order then updated_at.

        Args:
            db_path: Optional custom database path for testing.

        Returns:
            List of chat dicts with id, title, created_at, updated_at.
        """
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            try:
                cursor = await db.execute("""
                    SELECT id, title, created_at, updated_at
                    FROM chats
                    ORDER BY sort_order ASC, updated_at DESC
                """)
            except Exception:
                cursor = await db.execute("""
                    SELECT id, title, created_at, updated_at
                    FROM chats
                    ORDER BY updated_at DESC
                """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def delete(chat_id: str, db_path: Path = DB_PATH) -> bool:
        """Delete a chat and all its messages (via CASCADE).

        Args:
            chat_id: Chat identifier to delete.
            db_path: Optional custom database path for testing.

        Returns:
            True if the chat was found and deleted.
        """
        async with aiosqlite.connect(db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            cursor = await db.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
            await db.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.debug(f"Deleted chat {chat_id}")
            return deleted

    @staticmethod
    async def reorder(ordered_ids: List[str], db_path: Path = DB_PATH) -> None:
        """Update sort_order for all chats based on provided order.

        Args:
            ordered_ids: List of chat IDs in desired display order.
            db_path: Optional custom database path for testing.
        """
        async with aiosqlite.connect(db_path) as db:
            for index, chat_id in enumerate(ordered_ids):
                await db.execute("UPDATE chats SET sort_order = ? WHERE id = ?", (index, chat_id))
            await db.commit()
            logger.debug(f"Reordered {len(ordered_ids)} chats")

    @staticmethod
    async def get_count(db_path: Path = DB_PATH) -> int:
        """Get total number of chats.

        Args:
            db_path: Optional custom database path for testing.

        Returns:
            Integer count of all chats.
        """
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM chats")
            row = await cursor.fetchone()
            return row[0] if row else 0
