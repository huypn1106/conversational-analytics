"""
Stats Center — Redis Session Manager
Manages conversational state, history, and semantic routing context in Redis.
"""
from __future__ import annotations

import json
import uuid
import logging
from dataclasses import dataclass, field
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """In-memory representation of a chat session."""
    session_id: str
    history: list[dict] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    last_sql: str | None = None
    last_result: dict | None = None
    last_chart: dict | None = None

    def to_json(self) -> str:
        return json.dumps({
            "history": self.history,
            "context": self.context,
            "last_sql": self.last_sql,
            "last_result": self.last_result,
            "last_chart": self.last_chart,
        })

    @classmethod
    def from_json(cls, session_id: str, raw: str) -> SessionData:
        data = json.loads(raw)
        return cls(
            session_id=session_id,
            history=data.get("history", []),
            context=data.get("context", {}),
            last_sql=data.get("last_sql"),
            last_result=data.get("last_result"),
            last_chart=data.get("last_chart"),
        )


class RedisSessionManager:
    """
    Manages chat sessions in Redis with TTL-based expiration.

    Responsibilities:
    - Create / retrieve / update sessions
    - Store conversation history for follow-up context
    - Cache last query results for export/refinement
    """

    KEY_PREFIX = "session:"

    def __init__(self, redis: aioredis.Redis, ttl: int | None = None):
        self.redis = redis
        self.ttl = ttl or settings.SESSION_TTL_SECONDS

    def _key(self, session_id: str) -> str:
        return f"{self.KEY_PREFIX}{session_id}"

    async def create_session(self) -> SessionData:
        """Create a new session with a UUID."""
        session_id = str(uuid.uuid4())
        session = SessionData(session_id=session_id)
        await self.redis.setex(
            self._key(session_id),
            self.ttl,
            session.to_json(),
        )
        logger.info("Created session %s (TTL=%ds)", session_id, self.ttl)
        return session

    async def get_session(self, session_id: str) -> SessionData | None:
        """Retrieve an existing session, or None if expired/missing."""
        raw = await self.redis.get(self._key(session_id))
        if raw is None:
            return None
        # Refresh TTL on access
        await self.redis.expire(self._key(session_id), self.ttl)
        return SessionData.from_json(session_id, raw)

    async def save_session(self, session: SessionData) -> None:
        """Persist session state back to Redis."""
        await self.redis.setex(
            self._key(session.session_id),
            self.ttl,
            session.to_json(),
        )

    async def append_message(
        self, session_id: str, role: str, content: str
    ) -> SessionData | None:
        """Append a message to the session history."""
        session = await self.get_session(session_id)
        if session is None:
            return None
        session.history.append({"role": role, "content": content})
        await self.save_session(session)
        return session

    async def update_last_result(
        self,
        session_id: str,
        sql: str | None = None,
        result: dict | None = None,
        chart: dict | None = None,
    ) -> None:
        """Cache the last query result, SQL, and chart for follow-ups/export."""
        session = await self.get_session(session_id)
        if session is None:
            return
        if sql is not None:
            session.last_sql = sql
        if result is not None:
            session.last_result = result
        if chart is not None:
            session.last_chart = chart
        await self.save_session(session)

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        result = await self.redis.delete(self._key(session_id))
        return result > 0


class SemanticRouter:
    """
    Routes user messages to the appropriate pipeline based on intent.

    Intent categories:
    - CHART_QUERY:  NL → SQL → Data → Visualization
    - FOLLOW_UP:    Refine/modify last query using session context
    - CLARIFICATION: Ambiguous question — request more detail
    - EXPORT:       Export last results as CSV/JSON
    """

    INTENTS = ["chart_query", "follow_up", "clarification", "export"]

    def __init__(self, llm_service=None):
        self.llm = llm_service

    async def classify(self, message: str, session: SessionData | None = None, debug_list: list | None = None) -> str:
        """
        Classify user intent using the configured LLM.
        """
        msg_lower = message.lower().strip()

        if any(kw in msg_lower for kw in ["export", "download", "csv", "save as"]):
            return "export"

        if not session or not session.last_sql:
            if len(message.split()) < 3:
                return "clarification"
            return "chart_query"

        prompt = f"""You are an intent classification subsystem.
Given the new user message, classify it into exactly one of these intents:
1. chart_query: The user is asking a completely new, unrelated question about data.
2. follow_up: The user is asking to modify, filter, fix, format, or adjust the previous chart/query. They may say things like "change it to a pie chart", "what about EMEA?", "fix the colors", "too many rows", etc.
3. clarification: The prompt is too short, ambiguous, or lacks context to do anything.

User message: "{message}"

Return ONLY the exact intent string: "chart_query", "follow_up", or "clarification". No explanation."""

        messages = [{"role": "user", "content": prompt}]
        
        if debug_list is not None:
            debug_list.append({
                "step": "Intent Classification",
                "messages": messages.copy()
            })

        try:
            response = await self.llm.achat(messages=messages, max_tokens=10)
            intent = response.strip().lower()
            if intent in ["chart_query", "follow_up", "clarification"]:
                return intent
        except Exception as e:
            logger.warning("LLM intent routing failed (%s), falling back to heuristics.", e)

        # Fallback heuristic
        follow_up_cues = ["also", "what about", "how about", "change", "modify", "update", "filter", "add", "remove", "instead", "drill down", "by", "fix", "wrong", "make it", "show it", "pie", "bar", "line", "color"]
        if any(cue in msg_lower for cue in follow_up_cues):
            return "follow_up"
        return "chart_query"
