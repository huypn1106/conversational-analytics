"""
Stats Center — Application Configuration
Pydantic Settings for all environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Stats Center"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # ── StarRocks ─────────────────────────────────────────────────
    STARROCKS_HOST: str = "localhost"
    STARROCKS_PORT: int = 9030
    STARROCKS_USER: str = "root"
    STARROCKS_PASSWORD: str = ""
    STARROCKS_DATABASE: str = "stats_center"

    # ── Redis ─────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    SESSION_TTL_SECONDS: int = 1800  # 30 minutes

    # ── Ollama (OpenAI-compatible API) ──────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"
    OLLAMA_API_KEY: str = "ollama"  # Ollama ignores this but OpenAI client requires it
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 4096
    LLM_TIMEOUT_SECONDS: int = 120

    # ── Rate Limiting ─────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 30

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
