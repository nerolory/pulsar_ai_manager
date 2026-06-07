"""Model cache repository — caching provider models in SQLite."""

import json
from typing import List, Optional
from datetime import datetime

import aiosqlite
from loguru import logger

from app.paths import DB_PATH


class ModelCacheRepository:
    """Data access layer for the model_cache table.

    Provides methods for caching and retrieving provider model lists
    with TTL-based expiration.
    """

    @staticmethod
    async def cache(provider: str, models: List[dict]) -> None:
        """Cache models for a provider, replacing existing cache.

        Args:
            provider: Provider identifier.
            models: List of model dicts with id, name, context_length, etc.
        """
        now = int(datetime.now().timestamp() * 1000)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM model_cache WHERE provider = ?", (provider,))

            for model in models:
                pricing_json = json.dumps(model.get("pricing")) if model.get("pricing") else None
                await db.execute(
                    """
                    INSERT INTO model_cache
                        (provider, model_id, model_name, context_length, pricing,
                         free_tier, daily_limit, limit_tokens, balance, is_free, cached_at)
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

    @staticmethod
    async def get(provider: str, ttl_hours: int = 24) -> Optional[List[dict]]:
        """Get cached models for a provider if not expired.

        Args:
            provider: Provider identifier.
            ttl_hours: Cache time-to-live in hours (default 24).

        Returns:
            List of model dicts or None if cache is expired/empty.
        """
        ttl_ms = ttl_hours * 60 * 60 * 1000
        now = int(datetime.now().timestamp() * 1000)

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT model_id, model_name, context_length, pricing, free_tier,
                       daily_limit, limit_tokens, balance, is_free, cached_at
                FROM model_cache
                WHERE provider = ? AND cached_at > ?
                ORDER BY model_name
            """,
                (provider, now - ttl_ms),
            )

            rows = await cursor.fetchall()
            if not rows:
                return None

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
