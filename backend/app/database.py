import aiosqlite
from pathlib import Path
from typing import List, Optional, AsyncIterator
from loguru import logger
from datetime import datetime
import os

from app.paths import DB_PATH
from app.paths import BASE_DIR
from app.paths import MIGRATIONS_DIR


async def init_db() -> None:
    """Initialize database with tables and indexes"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        # Create schema_version table for migration tracking
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at INTEGER NOT NULL,
                description TEXT
            )
        """)

        await db.commit()

    # Run pending migrations
    await run_pending_migrations()

    # Create tables (if not already created by migrations)
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
            await db.execute(
                "UPDATE chats SET sort_order = rowid WHERE sort_order = 0 OR sort_order IS NULL"
            )
            await db.commit()
            logger.info("Migration: sort_order column added")
        except Exception:
            pass  # column already exists

        # Create model_cache table before optional column migrations
        await db.execute("""
            CREATE TABLE IF NOT EXISTS model_cache (
                provider TEXT NOT NULL,
                model_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                context_length INTEGER DEFAULT 4096,
                pricing TEXT,
                free_tier BOOLEAN DEFAULT 0,
                daily_limit INTEGER,
                limit_tokens INTEGER,
                balance REAL,
                is_free BOOLEAN DEFAULT 0,
                cached_at INTEGER NOT NULL,
                PRIMARY KEY (provider, model_id)
            )
        """)

        # Migration: add model limit columns to model_cache if missing
        try:
            await db.execute("ALTER TABLE model_cache ADD COLUMN daily_limit INTEGER")
            await db.commit()
            logger.info("Migration: daily_limit column added to model_cache")
        except Exception:
            pass  # column already exists

        try:
            await db.execute("ALTER TABLE model_cache ADD COLUMN limit_tokens INTEGER")
            await db.commit()
            logger.info("Migration: limit_tokens column added to model_cache")
        except Exception:
            pass  # column already exists

        try:
            await db.execute("ALTER TABLE model_cache ADD COLUMN balance REAL")
            await db.commit()
            logger.info("Migration: balance column added to model_cache")
        except Exception:
            pass  # column already exists

        try:
            await db.execute("ALTER TABLE model_cache ADD COLUMN is_free BOOLEAN DEFAULT 0")
            await db.commit()
            logger.info("Migration: is_free column added to model_cache")
        except Exception:
            pass  # column already exists

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_model_cache_provider 
            ON model_cache(provider, cached_at DESC)
        """)

        # Create model_groups table for grouping free/paid versions
        await db.execute("""
            CREATE TABLE IF NOT EXISTS model_groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT
            )
        """)

        await db.commit()
        logger.info("Database initialized successfully")


async def save_chat(chat_id: str, title: str) -> None:
    """Upsert chat metadata only — messages are saved separately via add_message"""
    now = int(datetime.now().timestamp() * 1000)

    async with aiosqlite.connect(DB_PATH) as db:
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


async def add_message(
    chat_id: str, msg_id: str, role: str, content: str, created_at: int, model: Optional[str] = None
) -> None:
    """Insert a single message and update chat updated_at"""
    now = int(datetime.now().timestamp() * 1000)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO messages (id, chat_id, role, content, created_at, model)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (msg_id, chat_id, role, content, created_at, model),
        )
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
        for index, chat_id in enumerate(ordered_ids):
            await db.execute("UPDATE chats SET sort_order = ? WHERE id = ?", (index, chat_id))
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


async def get_chat_messages(
    chat_id: str, limit: Optional[int] = None, before_rowid: Optional[int] = None
) -> List[dict]:
    """Get messages for a chat ordered by insertion (rowid). Pagination via before_rowid."""
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


async def cache_models(provider: str, models: List[dict]) -> None:
    """Cache models for a provider, replacing existing cache"""
    now = int(datetime.now().timestamp() * 1000)
    async with aiosqlite.connect(DB_PATH) as db:
        # Delete existing cache for this provider
        await db.execute("DELETE FROM model_cache WHERE provider = ?", (provider,))

        # Insert new models
        for model in models:
            import json

            pricing_json = json.dumps(model.get("pricing")) if model.get("pricing") else None
            await db.execute(
                """
                INSERT INTO model_cache (provider, model_id, model_name, context_length, pricing, free_tier, daily_limit, limit_tokens, balance, is_free, cached_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    provider,
                    model.get("id"),
                    model.get("name", model.get("id")),
                    model.get("context_length", 4096),
                    pricing_json,
                    model.get("free_tier", False),
                    model.get("daily_limit"),
                    model.get("limit_tokens"),
                    model.get("balance"),
                    model.get("is_free", False),
                    now,
                ),
            )

        await db.commit()
        logger.debug(f"Cached {len(models)} models for provider {provider}")


async def get_cached_models(provider: str, ttl_hours: int = 24) -> Optional[List[dict]]:
    """Get cached models for a provider if not expired"""
    ttl_ms = ttl_hours * 60 * 60 * 1000
    now = int(datetime.now().timestamp() * 1000)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT model_id, model_name, context_length, pricing, free_tier, daily_limit, limit_tokens, balance, is_free, cached_at
            FROM model_cache
            WHERE provider = ? AND cached_at > ?
            ORDER BY model_name
        """,
            (provider, now - ttl_ms),
        )

        rows = await cursor.fetchall()
        if not rows:
            return None

        import json

        result = []
        for row in rows:
            pricing = json.loads(row["pricing"]) if row["pricing"] else None
            result.append(
                {
                    "id": row["model_id"],
                    "name": row["model_name"],
                    "context_length": row["context_length"],
                    "pricing": pricing,
                    "free_tier": bool(row["free_tier"]),
                    "daily_limit": row["daily_limit"],
                    "limit_tokens": row["limit_tokens"],
                    "balance": row["balance"],
                    "is_free": bool(row["is_free"]),
                }
            )

        logger.debug(f"Retrieved {len(result)} cached models for provider {provider}")
        return result


async def get_current_schema_version() -> int:
    """Get current schema version from database"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT MAX(version) FROM schema_version")
        row = await cursor.fetchone()
        return row[0] if row and row[0] else 0


async def run_migration(version: int, description: str, sql: str) -> None:
    """Run a single migration and record it in schema_version"""
    now = int(datetime.now().timestamp() * 1000)
    async with aiosqlite.connect(DB_PATH) as db:
        # Execute migration SQL
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                await db.execute(statement)

        # Record migration
        await db.execute(
            "INSERT INTO schema_version (version, applied_at, description) VALUES (?, ?, ?)",
            (version, now, description),
        )
        await db.commit()
        logger.info(f"Migration {version} applied: {description}")


async def run_pending_migrations() -> None:
    """Run all pending migrations"""
    current_version = await get_current_schema_version()
    logger.info(f"Current schema version: {current_version}")

    # Get all migration files
    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory not found: {MIGRATIONS_DIR}")
        return

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    for migration_file in migration_files:
        # Extract version number from filename (e.g., 001_initial_schema.sql -> 1)
        try:
            version_str = migration_file.stem.split("_")[0]
            version = int(version_str)
        except (ValueError, IndexError):
            logger.warning(f"Invalid migration filename: {migration_file.name}")
            continue

        # Skip if already applied
        if version <= current_version:
            continue

        # Read migration SQL
        with open(migration_file, "r", encoding="utf-8") as f:
            sql = f.read()

        # Extract description from filename (e.g., 001_initial_schema.sql -> initial_schema)
        description = (
            migration_file.stem.split("_", 1)[1]
            if "_" in migration_file.stem
            else migration_file.stem
        )

        # Run migration
        try:
            await run_migration(version, description, sql)
        except Exception as e:
            logger.error(f"Migration {version} failed: {e}")
            raise


async def upgrade_schema(from_version: int, to_version: int) -> None:
    """Upgrade schema from one version to another"""
    current_version = await get_current_schema_version()

    if current_version != from_version:
        logger.warning(
            f"Current version {current_version} does not match expected from_version {from_version}"
        )

    await run_pending_migrations()

    new_version = await get_current_schema_version()
    if new_version != to_version:
        logger.warning(f"Expected version {to_version} but got {new_version}")
