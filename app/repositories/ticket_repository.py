# app/repositories/ticket_repository.py
from sqlalchemy import select

from app.models.ticket import Ticket
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    model = Ticket

    async def list_by_server(self, server_ip: str, limit: int = 10) -> list[Ticket]:
        result = await self.db.execute(
            select(Ticket).where(Ticket.server_ip == server_ip).limit(limit)
        )
        return list(result.scalars().all())