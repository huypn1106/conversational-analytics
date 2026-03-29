"""
Stats Center — Ollama LLM Service
OpenAI-compatible adapter for Qwen2.5-Coder served via Ollama.
"""
from __future__ import annotations

import logging
from typing import AsyncGenerator

from openai import OpenAI, AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class OllamaLlmService:
    """
    LLM service adapter that speaks the OpenAI Chat Completions API
    against a local Ollama server running Qwen2.5-Coder.

    Used by the Vanna agent for NL→SQL generation and chart reasoning.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        timeout: int | None = None,
    ):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.api_key = api_key or settings.OLLAMA_API_KEY
        self.temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

        # Synchronous client (for Vanna's internal calls)
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
        )

        # Async client (for streaming SSE responses)
        self.async_client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
        )

    def chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        **kwargs,
    ) -> str:
        """
        Synchronous chat completion.
        Returns the full response text.
        """
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        logger.debug(
            "Ollama chat request: model=%s, messages=%d",
            self.model,
            len(full_messages),
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs,
        )

        content = response.choices[0].message.content
        logger.debug("Ollama response: %s chars", len(content) if content else 0)
        return content or ""

    async def achat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        **kwargs,
    ) -> str:
        """
        Async chat completion.
        Returns the full response text.
        """
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        response = await self.async_client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs,
        )

        return response.choices[0].message.content or ""

    async def astream(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Async streaming chat completion.
        Yields token-by-token content deltas.
        """
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        stream = await self.async_client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def test_connection(self) -> bool:
        """Verify connectivity to the Ollama server."""
        try:
            models = self.client.models.list()
            return len(models.data) > 0
        except Exception:
            return False


# StarRocks-specific system prompt for SQL generation
STARROCKS_SYSTEM_PROMPT = """You are a data analytics SQL expert specializing in StarRocks.

Rules:
1. Generate valid StarRocks SQL (MySQL-compatible dialect).
2. Use the provided schema to form correct table and column names.
3. Always use column aliases for clarity.
4. For aggregations, always include a GROUP BY clause.
5. Limit results to 1000 rows unless explicitly asked otherwise.
6. Do NOT use CTEs if a simpler query works.
7. Prefer APPROX_COUNT_DISTINCT over COUNT(DISTINCT ...) for large datasets.
8. StarRocks supports: window functions, ARRAY/MAP/STRUCT types, materialized views.
9. Return ONLY the SQL query, no explanation.
"""
