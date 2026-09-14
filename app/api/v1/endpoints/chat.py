import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_chat_service, get_chat_service_with_tools
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
        request: ChatRequest,
        chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """对话接口：检索知识库 + 结合历史对话 + LLM生成回复。"""
    return await chat_service.ask(session_id=request.session_id, question=request.message)


# app/api/v1/endpoints/chat.py（新增一个走工具调用的接口）
@router.post("/chat/agent", response_model=ChatResponse)
async def chat_with_tools(
        request: ChatRequest,
        chat_service: ChatService = Depends(get_chat_service_with_tools),
) -> ChatResponse:
    return await chat_service.ask_with_tools(session_id=request.session_id, question=request.message)


@router.post("/chat/stream", summary="流式对话接口")
async def chat_stream(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service_with_tools)):
    """流式对话接口：检索知识库 + 结合历史对话 + LLM生成回复，使用SSE流式返回结果。"""

    async def event_generator():
        async for chunk in chat_service.ask_stream(session_id=request.session_id, question=request.message):
            event_type = chunk.get("event", "message")
            payload = {k: v for k, v in chunk.items() if k != "event"}
            yield f"event: {event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/session/{session_id}", summary="获取会话历史")
async def get_session(session_id: str, chat_service: ChatService = Depends(get_chat_service)):
    return await chat_service.get_session_history(session_id)


@router.get("/session", summary="列出所有会话ID")
async def list_sessions(chat_service: ChatService = Depends(get_chat_service)):
    # This is a placeholder implementation - you should replace it with the actual logic to list all session IDs
    return await chat_service.list_sessions()


@router.delete("/session/{session_id}", summary="删除会话历史")
async def delete_session(session_id: str, chat_service: ChatService = Depends(get_chat_service)):
    return await chat_service.delete_session(session_id)
