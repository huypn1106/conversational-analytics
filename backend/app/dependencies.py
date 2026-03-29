"""
Stats Center — FastAPI Dependencies
Provides shared resources (Redis, DB connections) via dependency injection.
"""
from functools import lru_cache
from typing import AsyncGenerator

import redis.asyncio as aioredis

from app.config import settings
from core.vanna_agent import VannaAgent


@lru_cache()
def get_settings():
    """Return cached application settings."""
    return settings


_vanna_agent: VannaAgent | None = None

async def get_agent() -> VannaAgent:
    """Return a shared singleton instance of the VannaAgent."""
    global _vanna_agent
    if _vanna_agent is None:
        _vanna_agent = VannaAgent()
        # Prefetch the schema in the background to speed up first query
        import asyncio
        asyncio.create_task(_vanna_agent.load_schema())
    return _vanna_agent


_redis_pool: aioredis.Redis | None = None


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Yield a Redis connection from the shared pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    yield _redis_pool


async def init_redis() -> aioredis.Redis:
    """Initialize the Redis connection pool (called at startup)."""
    global _redis_pool
    _redis_pool = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    # Verify connectivity
    await _redis_pool.ping()
    return _redis_pool


async def close_redis():
    """Close the Redis connection pool (called at shutdown)."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.close()
        _redis_pool = None
