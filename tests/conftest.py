from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """用于 e2e 测试的异步 HTTP 客户端，不用真实起服务进程。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_llm_client():
    """单元测试里替换掉真实的 DeepSeek 调用，避免测试依赖网络。"""
    mock = AsyncMock()
    mock.chat.return_value = "这是模拟的LLM回复"
    return mock
