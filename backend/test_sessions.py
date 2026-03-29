import asyncio
import redis.asyncio as aioredis
from core.redis_session import RedisSessionManager
from app.config import settings

async def main():
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=False)
        manager = RedisSessionManager(r, ttl=settings.SESSION_TTL_SECONDS)
        sessions = await manager.get_all_sessions()
        for session in sessions:
            print(f"Session {session.session_id} - {session.title}")
        await r.close()
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
