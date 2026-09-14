from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """通用 Repository 基类，面向单个聚合根，封装基础的增删改查。
    具体聚合的特殊查询（比如按 session_id 查会话）在子类里加专门的方法，
    不要把跨聚合的任意查询堆在这里。
    """

    model: type[ModelType]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: int) -> ModelType | None:
        return await self.db.get(self.model, id)

    async def add(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def list_all(self, limit: int = 100) -> list[ModelType]:
        result = await self.db.execute(select(self.model).limit(limit))
        return list(result.scalars().all())
