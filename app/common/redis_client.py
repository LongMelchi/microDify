"""Redis client wrapper — async connection pool, JSON serialization, rate-limit helpers.

Usage::

    from app.common.redis_client import RedisClient, get_redis

    # In a FastAPI endpoint:
    @router.get("/example")
    async def example(redis: RedisClient | None = Depends(get_redis)):
        await redis.set("key", {"foo": "bar"}, ttl=3600)
        value = await redis.get("key")      # → {"foo": "bar"}
        current  = await redis.incr("cnt")  # → 1
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

from app.core.config import get_settings

settings = get_settings()

# ── Connection pool (lazily initialised) ──────────────────────────────────────

_pool: ConnectionPool | None = None


def _get_pool() -> ConnectionPool:
    """Return a module-level connection pool, creating it on first access."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=20,
            decode_responses=True,
        )
    return _pool


async def get_redis() -> RedisClient | None:
    """FastAPI dependency — returns a ``RedisClient`` or ``None`` if Redis is unavailable."""
    import structlog

    logger = structlog.get_logger("microdify.redis")

    if not settings.redis_url:
        return None
    try:
        pool = _get_pool()
        client = aioredis.Redis(connection_pool=pool)
        await client.ping()
        return RedisClient(client)
    except Exception:
        logger.warning("Redis unavailable, skipping", exc_info=True)
        return None


# ── Serialisation helpers ─────────────────────────────────────────────────────


def _serialize(value: dict | list | str) -> str:
    """Encode a Python object as a JSON string for Redis storage."""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def _deserialize(raw: str | None) -> dict | list | str | None:
    """Decode a Redis (JSON) string back to a Python object."""
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


# ── Redis client wrapper ──────────────────────────────────────────────────────


class RedisClient:
    """Thin async wrapper around a :class:`redis.asyncio.Redis` connection.

    All values are transparently serialised to JSON strings on write and parsed
    back on read.  TTLs are in **seconds**.
    """

    def __init__(self, client: aioredis.Redis) -> None:
        self._client = client

    # ── Key-value helpers ───────────────────────────────────────────────────

    async def get(self, key: str) -> dict | list | str | None:
        """Read and deserialise a JSON value from *key*."""
        raw = await self._client.get(key)
        return _deserialize(raw)

    async def set(self, key: str, value: dict | list | str, *, ttl: int | None = None) -> None:
        """Serialise *value* to JSON and write it to *key* with an optional *ttl*."""
        payload = _serialize(value)
        if ttl is not None:
            await self._client.setex(key, ttl, payload)
        else:
            await self._client.set(key, payload)

    async def delete(self, key: str) -> None:
        """Remove *key* from Redis."""
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        """Return ``True`` if *key* is present."""
        return bool(await self._client.exists(key))

    async def expire(self, key: str, ttl: int) -> None:
        """Set or update the TTL (seconds) for an existing *key*."""
        await self._client.expire(key, ttl)

    async def incr(self, key: str, amount: int = 1) -> int:
        """Atomically increment *key* by *amount* and return the new value."""
        return await self._client.incrby(key, amount)

    # ── Rate-limiter primitives ─────────────────────────────────────────────

    async def check_rate_limit(
        self, user_id: str, action: str, max_count: int, window_seconds: int
    ) -> bool:
        """Return ``True`` if *user_id* is still under the rate limit for *action*.

        Uses a rolling-window counter with auto-expiry.  Call this before
        performing an expensive operation (LLM call, file parse, etc.).
        """
        key = f"rate_limit:{action}:{user_id}"
        current = await self._client.incr(key)
        if current == 1:
            await self._client.expire(key, window_seconds)
        return current <= max_count

    # ── Queue primitives (for async doc processing) ─────────────────────────

    async def enqueue(self, queue_name: str, item: dict) -> None:
        """Push a JSON-serialisable *item* onto a Redis list (FIFO queue)."""
        await self._client.lpush(queue_name, _serialize(item))

    async def dequeue(self, queue_name: str, timeout: int = 5) -> dict | None:
        """Block for up to *timeout* seconds to pop the next item from the queue."""
        _, raw = await self._client.brpop(queue_name, timeout)
        result = _deserialize(raw)
        return result if isinstance(result, dict) else None
