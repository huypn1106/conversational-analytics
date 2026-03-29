"""
Stats Center — Health Check Router
Verifies connectivity to Redis, StarRocks, and Ollama.
"""
from fastapi import APIRouter, Depends
import redis.asyncio as aioredis
import httpx

from app.dependencies import get_redis, get_settings
from app.config import Settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
):
    """Return service health status for all upstream dependencies."""
    status = {"status": "ok", "services": {}}

    # ── Redis ─────────────────────────────────────────────────
    try:
        await redis.ping()
        status["services"]["redis"] = "healthy"
    except Exception as exc:
        status["services"]["redis"] = f"unhealthy: {exc}"
        status["status"] = "degraded"

    # ── StarRocks ─────────────────────────────────────────────
    try:
        import pymysql

        conn = pymysql.connect(
            host=cfg.STARROCKS_HOST,
            port=cfg.STARROCKS_PORT,
            user=cfg.STARROCKS_USER,
            password=cfg.STARROCKS_PASSWORD,
            database=cfg.STARROCKS_DATABASE,
            connect_timeout=5,
        )
        conn.cursor().execute("SELECT 1")
        conn.close()
        status["services"]["starrocks"] = "healthy"
    except Exception as exc:
        status["services"]["starrocks"] = f"unhealthy: {exc}"
        status["status"] = "degraded"

    # ── Ollama ─────────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{cfg.OLLAMA_BASE_URL}/models")
            resp.raise_for_status()
        status["services"]["ollama"] = "healthy"
    except Exception as exc:
        status["services"]["ollama"] = f"unhealthy: {exc}"
        status["status"] = "degraded"

    return status
