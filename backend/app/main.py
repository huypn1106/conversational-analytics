"""
Stats Center — FastAPI Application Entrypoint
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.dependencies import init_redis, close_redis
from app.routers import health, chat

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle events."""
    logger.info("🚀 Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

    # ── Startup ───────────────────────────────────────────────
    try:
        await init_redis()
        logger.info("✅ Redis connected")
    except Exception as exc:
        logger.warning("⚠️  Redis unavailable at startup: %s", exc)

    yield

    # ── Shutdown ──────────────────────────────────────────────
    await close_redis()
    logger.info("👋 %s shut down cleanly", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Conversational Analytics Platform — NL → SQL → Interactive Charts",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
