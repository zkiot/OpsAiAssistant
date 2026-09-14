# app/services/ticket_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository

VALID_SEVERITY = {"P1", "P2", "P3", "P4"}


class TicketService:
    """按 CMDBService 同样的思路：既支持依赖注入传入 db session，
    也支持独立创建自己的 session（MCP工具场景下没有请求级别的session可用）。
    """

    def __init__(self, db: AsyncSession | None = None):
        self._db = db

    async def create_ticket(
        self, server_ip: str, title: str, description: str, severity: str = "P3"
    ) -> Ticket:
        severity = severity.upper() if severity.upper() in VALID_SEVERITY else "P3"
        ticket = Ticket(server_ip=server_ip, title=title, description=description, severity=severity)

        if self._db is not None:
            repo = TicketRepository(self._db)
            await repo.add(ticket)
            await self._db.commit()
            return ticket

        # 没有外部传入session时（比如MCP工具场景），自己管理一个独立事务
        async with async_session_maker() as session:
            repo = TicketRepository(session)
            await repo.add(ticket)
            await session.commit()
            return ticket

    async def create_ticket_as_text(
        self, server_ip: str, title: str, description: str, severity: str = "P3"
    ) -> str:
        """给 LLM/MCP 工具用的文本格式化版本。"""
        ticket = await self.create_ticket(server_ip, title, description, severity)
        return (
            f"工单创建成功：工单号 {ticket.id}，"
            f"服务器 {ticket.server_ip}，严重级别 {ticket.severity}，"
            f"标题「{ticket.title}」，当前状态「{ticket.status}」"
        )

    async def get_ticket(self, ticket_id: str) -> Ticket:
        if self._db is not None:
            repo = TicketRepository(self._db)
            ticket = await repo.get_by_id(ticket_id)
            return ticket

        async with async_session_maker() as session:
            repo = TicketRepository(session)
            ticket = await repo.get_by_id(ticket_id)
            return ticket

    async def list_tickets(self, limit: int = 10, offset: int = 0) -> list[Ticket]:
        if self._db is not None:
            repo = TicketRepository(self._db)
            tickets = await repo.list_all(limit=limit)
            return tickets

        async with async_session_maker() as session:
            repo = TicketRepository(session)
            tickets = await repo.list_all(limit=limit)
            return tickets

    async def list_tickets_by_server(self, server_ip: str, limit: int = 10, offset: int = 0) -> list[Ticket]:
        if self._db is not None:
            repo = TicketRepository(self._db)
            tickets = await repo.list_by_server(server_ip=server_ip, limit=limit)
            return tickets

        async with async_session_maker() as session:
            repo = TicketRepository(session)
            tickets = await repo.list_by_server(server_ip=server_ip, limit=limit)
            return tickets