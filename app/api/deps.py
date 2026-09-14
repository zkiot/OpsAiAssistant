from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService
from app.services.memory_service import MemoryService
from app.core.mcp_pool import mcp_pool
from app.infrastructure.mcp.mcp_client import MCPToolClient
from pathlib import Path
from app.services.ticket_service import TicketService


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # app/api/deps.py 往上三级到项目根目录


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_chat_service() -> ChatService:
    # 无状态服务，直接构造；如果服务本身有需要复用的连接池，可以考虑做成单例
    return ChatService()

def get_memory_service() -> MemoryService:
    return MemoryService()

def get_rag_service() -> RAGService:
    return RAGService()

def get_chat_service_with_tools() -> ChatService:
    return ChatService(mcp_client=MCPToolClient(mcp_pool))

async def get_ticket_service(db: AsyncSession = Depends(get_db)) -> TicketService:
    return TicketService(db=db)   # 传入请求级别的db session，走同一个事务