from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的基类，alembic 也依赖这个 metadata 做迁移自动生成。"""

    pass
