import aiosqlite
from pathlib import Path
from typing import List, Optional, AsyncIterator
from loguru import logger
from datetime import datetime

DB_PATH = Path("/app/data/chats.db")

async def init_db() -> None:
    """Initialize database with tables and indexes"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Create chats table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """)
        
        # Create messages table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                model TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for performance
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_chat_created 
            ON messages(chat_id, created_at DESC)
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_chats_updated 
            ON chats(updated_at DESC)
        """)
        
        # Migration: add sort_order column if missing
        try:
            await db.execute("ALTER TABLE chats ADD COLUMN sort_order INTEGER DEFAULT 0")
            await db.commit()
            await db.execute("UPDATE chats SET sort_order = rowid WHERE sort_order = 0 OR sort_order IS NULL")
            await db.commit()
            logger.info("Migration: sort_order column added")
        except Exception:
            pass  # column already exists

        await db.commit()
        logger.info("Database initialized successfully")

async def save_chat(chat_id: str, title: str, messages: List[dict] = []) -> None:
    """Upsert chat metadata only — messages are saved separately via add_message"""
    now = int(datetime.now().timestamp() * 1000)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO chats (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                updated_at = excluded.updated_at
        """, (chat_id, title, now, now))
        await db.commit()
        logger.debug(f"Upserted chat {chat_id}")

async def add_message(chat_id: str, msg_id: str, role: str, content: str, created_at: int, model: Optional[str] = None) -> None:
    """Insert a single message and update chat updated_at"""
    now = int(datetime.now().timestamp() * 1000)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO messages (id, chat_id, role, content, created_at, model)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (msg_id, chat_id, role, content, created_at, model))
        await db.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
        await db.commit()
        logger.debug(f"Added message {msg_id} role={role} to chat {chat_id}")

async def update_message_content(msg_id: str, content: str) -> None:
    """Update content of existing message (e.g. completed assistant response)"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE messages SET content = ? WHERE id = ?", (content, msg_id))
        await db.commit()

async def reorder_chats(ordered_ids: List[str]) -> None:
    """Update sort_order for all chats based on provided order"""
    async with aiosqlite.connect(DB_PATH) as db:
        for idx, chat_id in enumerate(ordered_ids):
            await db.execute("UPDATE chats SET sort_order = ? WHERE id = ?", (idx, chat_id))
        await db.commit()
        logger.debug(f"Reordered {len(ordered_ids)} chats")

async def get_chat_list() -> List[dict]:
    """Get all chats ordered by sort_order then updated_at"""
    async with aiosqlite.connect(DB_PATH) as db:
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

async def get_chat_messages(chat_id: str, limit: Optional[int] = None, before_rowid: Optional[int] = None) -> List[dict]:
    """Get messages for a chat ordered by insertion (rowid). Pagination via before_rowid."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        params: list = [chat_id]

        if before_rowid is not None:
            params.append(before_rowid)
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
                params.append(limit)
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
                params.append(limit)
            else:
                query = """
                    SELECT id, role, content, created_at, model, rowid
                    FROM messages
                    WHERE chat_id = ?
                    ORDER BY rowid ASC
                """

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def clear_chat_messages(chat_id: str) -> None:
    """Delete all messages for a chat without deleting the chat itself"""
    now = int(datetime.now().timestamp() * 1000)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        await db.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
        await db.commit()
        logger.debug(f"Cleared messages for chat {chat_id}")

async def delete_chat(chat_id: str) -> bool:
    """Delete a chat and all its messages"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        await db.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.debug(f"Deleted chat {chat_id}")
        return deleted

async def get_chat_count() -> int:
    """Get total number of chats"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM chats")
        row = await cursor.fetchone()
        return row[0] if row else 0
