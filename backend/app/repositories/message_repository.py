"""Message repository — CRUD operations for messages table."""

from typing import List, Optional
from datetime import datetime

import aiosqlite
from loguru import logger

from app.paths import DB_PATH


class MessageRepository:
    """Data access layer for the messages table.

    Provides methods for adding, updating, querying and deleting messages.
    """

    @staticmethod
    async def add(
        chat_id: str,
        msg_id: str,
        role: str,
        content: str,
        created_at: int,
        model: Optional[str] = None,
    ) -> None:
        """Insert a single message and update chat's updated_at.

        Args:
            chat_id: Parent chat identifier.
            msg_id: Unique message identifier.
            role: Message role (user, assistant, system).
            content: Message content (text or JSON).
            created_at: Timestamp in milliseconds.
            model: Optional model name that generated the message.
        """
        now = int(datetime.now().timestamp() * 1000)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT OR IGNORE INTO messages (id, chat_id, role, content, created_at, model)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (msg_id, chat_id, role, content, created_at, model))
            await db.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
            await db.commit()
            logger.debug(f"Added message {msg_id} role={role} to chat {chat_id}")

    @staticmethod
    async def update_content(msg_id: str, content: str) -> None:
        """Update content of an existing message.

        Args:
            msg_id: Message identifier.
            content: New content to set.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE messages SET content = ? WHERE id = ?", (content, msg_id))
            await db.commit()

    @staticmethod
    async def get_by_chat(
        chat_id: str,
        limit: Optional[int] = None,
        before_rowid: Optional[int] = None,
    ) -> List[dict]:
        """Get messages for a chat ordered by insertion (rowid).

        Supports pagination via before_rowid for infinite scroll.

        Args:
            chat_id: Parent chat identifier.
            limit: Maximum number of messages to return.
            before_rowid: Only return messages with rowid less than this.

        Returns:
            List of message dicts with id, role, content, created_at, model, rowid.
        """
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            query_params: list = [chat_id]

            if before_rowid is not None:
                query_params.append(before_rowid)
                if limit is not None:
                    query = """
                        SELECT * FROM (
                            SELECT id, role, content, created_at, model, rowid
                            FROM messages
                            WHERE chat_id = ? AND rowid < ?
                            ORDER BY rowid DESC
                            LIMIT ?
                        ) ORDER BY rowid ASC
                    """
                    query_params.append(limit)
                else:
                    query = """
                        SELECT id, role, content, created_at, model, rowid
                        FROM messages
                        WHERE chat_id = ? AND rowid < ?
                        ORDER BY rowid ASC
                    """
            else:
                if limit is not None:
                    query = """
                        SELECT * FROM (
                            SELECT id, role, content, created_at, model, rowid
                            FROM messages
                            WHERE chat_id = ?
                            ORDER BY rowid DESC
                            LIMIT ?
                        ) ORDER BY rowid ASC
                    """
                    query_params.append(limit)
                else:
                    query = """
                        SELECT id, role, content, created_at, model, rowid
                        FROM messages
                        WHERE chat_id = ?
                        ORDER BY rowid ASC
                    """

            cursor = await db.execute(query, query_params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def clear_by_chat(chat_id: str) -> None:
        """Delete all messages for a chat without deleting the chat itself.

        Args:
            chat_id: Parent chat identifier.
        """
        now = int(datetime.now().timestamp() * 1000)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            await db.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
            await db.commit()
            logger.debug(f"Cleared messages for chat {chat_id}")
