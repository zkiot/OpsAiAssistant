import json

import pytest

from app.services.memory_service import MemoryService


class FakeRedis:
    def __init__(self):
        self.data = {
            "chat_history:s1": [json.dumps({"role": "user", "content": "hi"}), json.dumps({"role": "assistant", "content": "hello"})],
            "chat_history:s2": [json.dumps({"role": "user", "content": "again"})],
        }

    async def keys(self, pattern: str):
        async def _iter():
            for key in self.data:
                yield key

        return _iter()

    async def llen(self, key: str) -> int:
        return len(self.data.get(key, []))

    async def get(self, key: str):
        if key == "total_requests":
            return "7"
        if key == "system_start_time":
            return "100"
        return None

    async def delete(self, key: str):
        self.data.pop(key, None)


@pytest.mark.asyncio
async def test_memory_service_stats_handles_async_key_generators():
    service = object.__new__(MemoryService)
    service._redis = FakeRedis()
    service._max_turns = 10

    sessions = await service.list_sessions()
    stats = await service.stats()

    assert [session["session_id"] for session in sessions] == ["s1", "s2"]
    assert stats["active_sessions"] == 2
    assert stats["total_messages"] == 3
    assert stats["total_requests"] == 7
    assert stats["uptime_seconds"] >= 0
