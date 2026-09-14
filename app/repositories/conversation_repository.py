from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_session_id(self, session_id: str) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, session_id: str) -> Conversation:
        conv = await self.get_by_session_id(session_id)
        if conv is None:
            conv = Conversation(session_id=session_id)
            await self.add(conv)
        return conv

    async def append_message(self, conversation: Conversation, role: str, content: str) -> Message:
        msg = Message(conversation_id=conversation.id, role=role, content=content)
        self.db.add(msg)
        await self.db.flush()
        return msg
