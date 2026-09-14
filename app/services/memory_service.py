import json
import logging
import time
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


class MemoryService:
    """短期会话记忆：把最近N轮对话存 Redis，带过期时间。"""

    def __init__(self, max_turns: int = 10):
        self._redis = get_redis()
        self._max_turns = max_turns

    def _key(self, session_id: str) -> str:
        return f"chat_history:{session_id}"

    async def add_message(self, session_id: str, role: str, content: str) -> None:
        key = self._key(session_id)
        await self._redis.rpush(key, json.dumps({"role": role, "content": content}))
        await self._redis.ltrim(key, -self._max_turns * 2, -1)
        await self._redis.expire(key, settings.SESSION_TTL_SECONDS)

    async def get_history(self, session_id: str) -> list[dict]:
        raw = await self._redis.lrange(self._key(session_id), 0, -1)
        return [json.loads(x) for x in raw]

    async def _session_keys(self) -> list[str]:
        keys = await self._redis.keys("chat_history:*")
        if keys is None:
            return []
        if hasattr(keys, "__aiter__"):
            return [key async for key in keys]
        return list(keys)

    async def list_sessions(self) -> list[dict]:
        sessions = []
        for key in await self._session_keys():
            raw = await self._redis.lrange(key, 0, 1)
            first_message = json.loads(raw[0]) if raw else None
            sessions.append({
                "session_id": key.split(":", 1)[1],
                "name": first_message.get("content","") if first_message else key.split(":", 1)[1],
                "message_count": await self._redis.llen(key),
            })
        return sessions

    async def delete_session(self, session_id: str) -> None:
        await self._redis.delete(self._key(session_id))

    async def health(self) -> dict:
        return {"status": "ok"}

    async def stats(self) -> dict:
        keys = await self._session_keys()
        total_messages = 0
        for key in keys:
            total_messages += await self._redis.llen(key)

        total_requests = await self._redis.get("total_requests") or 0
        system_start_time = await self._redis.get("system_start_time") or 0

        return {
            "uptime_seconds": int(time.time() - int(system_start_time or 0)),
            "total_requests": int(total_requests) if total_requests is not None else 0,
            "active_sessions": len(await self.list_sessions()),
            "total_messages": total_messages,
            "tools_available": 0,
        }
