from unittest.mock import AsyncMock

import pytest

from app.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_ask_returns_answer_and_updates_memory(mock_llm_client):
    """单元测试：Mock掉LLM/RAG/Memory，只验证 ChatService 的编排逻辑本身。"""
    mock_rag = AsyncMock()
    mock_rag.retrieve.return_value = [{"text": "磁盘告警先检查挂载点", "category": "故障处理", "score": 0.9}]

    mock_memory = AsyncMock()
    mock_memory.get_history.return_value = []

    service = ChatService(llm_client=mock_llm_client, rag_service=mock_rag, memory_service=mock_memory)

    response = await service.ask(session_id="test-session", question="磁盘满了怎么办")

    assert response.message == "这是模拟的LLM回复"
    assert response.session_id == "test-session"
    assert len(response.sources) == 1

    mock_rag.retrieve.assert_awaited_once()
    mock_memory.add_message.assert_any_call("test-session", "user", "磁盘满了怎么办")
    mock_memory.add_message.assert_any_call("test-session", "assistant", "这是模拟的LLM回复")
