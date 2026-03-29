"""
Stats Center — SSE Chat Router
Handles conversational analytics queries, streaming responses via Server-Sent Events.
"""
import json
import uuid
import asyncio
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import redis.asyncio as aioredis
from app.dependencies import get_redis, get_settings, get_agent
from app.config import Settings
from core.vanna_agent import VannaAgent
from core.redis_session import RedisSessionManager, SemanticRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


# ── Request / Response Models ─────────────────────────────────────

class ChatRequest(BaseModel):
    """Incoming chat message from the frontend."""
    session_id: str | None = Field(
        default=None,
        description="Existing session ID. If omitted, a new session is created.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language question from the user.",
    )


class SessionResponse(BaseModel):
    """Response when creating or retrieving a session."""
    session_id: str
    created: bool = False

class FolderCreateRequest(BaseModel):
    name: str

class SessionPatchRequest(BaseModel):
    folder_id: str | None = None


# ── SSE Helpers ───────────────────────────────────────────────────

def sse_event(event_type: str, data: object) -> str:
    """Format a single SSE event string."""
    payload = json.dumps({"type": event_type, "data": data}, default=str)
    return f"data: {payload}\n\n"


# ── Endpoints ─────────────────────────────────────────────────────

@router.get("/sessions")
async def get_all_sessions(
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
):
    """Retrieve all existing chat sessions for the active user/browser."""
    manager = RedisSessionManager(redis, ttl=cfg.SESSION_TTL_SECONDS)
    sessions = await manager.get_all_sessions()
    
    return [
        {
            "session_id": s.session_id,
            "title": s.title,
            "folder_id": s.folder_id,
            "created_at": s.created_at,
        }
        for s in sessions
    ]

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
):
    manager = RedisSessionManager(redis, ttl=cfg.SESSION_TTL_SECONDS)
    deleted = await manager.delete_session(session_id)
    return {"deleted": deleted}

@router.patch("/sessions/{session_id}")
async def patch_session(
    session_id: str,
    body: SessionPatchRequest,
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
):
    manager = RedisSessionManager(redis, ttl=cfg.SESSION_TTL_SECONDS)
    updated = await manager.move_session(session_id, body.folder_id)
    return {"updated": updated}

@router.get("/folders")
async def get_all_folders(
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
):
    manager = RedisSessionManager(redis, ttl=cfg.SESSION_TTL_SECONDS)
    folders = await manager.get_all_folders()
    return [{"id": f.id, "name": f.name} for f in folders]

@router.post("/folders")
async def create_folder(
    body: FolderCreateRequest,
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
):
    manager = RedisSessionManager(redis, ttl=cfg.SESSION_TTL_SECONDS)
    folder = await manager.create_folder(body.name)
    return {"id": folder.id, "name": folder.name}

@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: str,
    delete_conversations: bool = False,
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
):
    manager = RedisSessionManager(redis, ttl=cfg.SESSION_TTL_SECONDS)
    await manager.delete_folder(folder_id, delete_conversations=delete_conversations)
    return {"deleted": True}


@router.post("/sessions")
async def create_session(
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
) -> SessionResponse:
    """Create a new chat session."""
    manager = RedisSessionManager(redis, ttl=cfg.SESSION_TTL_SECONDS)
    session = await manager.create_session()
    return SessionResponse(session_id=session.session_id, created=True)


@router.post("/chat")
async def chat_sse(
    body: ChatRequest,
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
    agent: VannaAgent = Depends(get_agent),
):
    """
    Main conversational endpoint.
    Accepts a natural-language question and streams back typed SSE events:
      - status   : progress updates
      - sql      : generated SQL string
      - table    : { columns: [...], rows: [...] }
      - plotly_chart : { data: [...], layout: {...} }
      - summary  : natural language summary
      - error    : { message, code }
      - done     : null
    """
    # Resolve or create session
    manager = RedisSessionManager(redis, ttl=cfg.SESSION_TTL_SECONDS)
    if body.session_id:
        session = await manager.get_session(body.session_id)
        if session is None:
            # Recreate session with same ID if expired
            session = await manager.create_session()
            session.session_id = body.session_id
            await manager.save_session(session)
    else:
        session = await manager.create_session()
        
    if session.title == "New Conversation":
        session.title = body.message[:40] + ("..." if len(body.message) > 40 else "")
        await manager.save_session(session)

    session_id = session.session_id
    
    # Analyze intent
    semantic_router = SemanticRouter(agent.llm)
    debug_list = []
    intent = await semantic_router.classify(body.message, session, debug_list=debug_list)
    logger.info("Classified intent: %s for query: %s", intent, body.message)

    # Append user message to history
    await manager.append_message(session_id, "user", body.message)
    session = await manager.get_session(session_id)

    async def event_stream() -> AsyncGenerator[str, None]:
        """Generate SSE events by running the Vanna agent pipeline."""
        try:
            # ── Phase 1: Emit session acknowledgement ─────────
            yield sse_event("status", {"session_id": session_id, "message": "Processing your question..."})
            
            # Emit intent classification debug if available
            while debug_list:
                yield sse_event("debug", debug_list.pop(0))

            # Handle non-query intents quickly
            if intent == "clarification":
                msg = "Could you please provide a few more details? I want to make sure I pull the right data for you."
                yield sse_event("summary", msg)
                await manager.append_message(session_id, "assistant", msg)
                yield sse_event("done", None)
                return
            
            if intent == "export":
                msg = "I've noted you want to export. (Data export will be fully supported in Phase 3!)"
                yield sse_event("summary", msg)
                await manager.append_message(session_id, "assistant", msg)
                yield sse_event("done", None)
                return

            # ── Phase 2: Agent pipeline ──
            yield sse_event("status", "Analyzing database schema...")
            if not agent.schema_ddl:
                await agent.load_schema()
            
            yield sse_event("status", "Generating SQL query...")
            # For follow-ups, we can inject last_sql into context
            history = session.history[:-1] # Exclude the current question we just appended
            if intent == "follow_up" and session.last_sql:
                system_msg = (
                    f"The user is asking a follow-up to their previous query. "
                    f"Previous SQL:```sql\n{session.last_sql}\n```\n"
                    f"If the user is ONLY asking to change the chart type or styling (e.g., 'make it a pie chart'), "
                    f"you MUST output the EXACT SAME previous SQL query. "
                    f"If the user is asking to filter or change the DATA, modify the SQL accordingly. "
                    f"Output ONLY valid SQL code."
                )
                history.append({"role": "system", "content": system_msg})
            sql = await agent.generate_sql(body.message, history, debug_list=debug_list)
            while debug_list:
                yield sse_event("debug", debug_list.pop(0))
            yield sse_event("sql", sql)

            yield sse_event("status", "Executing query against StarRocks...")
            results = await agent.execute_sql(sql)
            
            # Send data table
            chart = None
            if results["row_count"] > 0:
                yield sse_event("table", {
                    "columns": results["columns"],
                    "rows": results["rows"],
                })
                
                # Optionally generate chart and summary only if we have data
                yield sse_event("status", "Preparing interactive chart...")
                chart = await agent.generate_chart(body.message, results["columns"], results["rows"], context=history, debug_list=debug_list)
                while debug_list:
                    yield sse_event("debug", debug_list.pop(0))
                yield sse_event("plotly_chart", chart)
                
                yield sse_event("status", "Synthesizing insights...")
                summary = await agent.generate_summary(body.message, results["columns"], results["rows"], debug_list=debug_list)
                while debug_list:
                    yield sse_event("debug", debug_list.pop(0))
                yield sse_event("summary", summary)
            else:
                summary = "The query executed successfully but returned zero rows."
                yield sse_event("summary", summary)

            # ── Phase 3: Persist session ──────────────────────
            await manager.append_message(session_id, "assistant", summary)
            await manager.update_last_result(session_id, sql=sql, result=results, chart=chart)

            yield sse_event("done", None)

        except Exception as exc:
            logger.exception("Chat pipeline error")
            yield sse_event("error", {"message": str(exc), "code": "PIPELINE_ERROR"})
            yield sse_event("done", None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Session-Id": session_id,
        },
    )


@router.get("/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    redis: aioredis.Redis = Depends(get_redis),
    cfg: Settings = Depends(get_settings),
):
    """Retrieve conversation history for a session."""
    manager = RedisSessionManager(redis, ttl=cfg.SESSION_TTL_SECONDS)
    session = await manager.get_session(session_id)
    if session is None:
        return {"session_id": session_id, "history": [], "found": False}

    return {
        "session_id": session_id,
        "history": session.history,
        "found": True,
    }
