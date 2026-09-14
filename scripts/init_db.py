"""开发环境快速建表脚本（生产环境请用 alembic migration，不要用这个）。

用法: python -m scripts.init_db
"""

import asyncio

from app.db.base import Base
from app.db.session import engine
from app.models import conversation, document  # noqa: F401  确保模型被注册


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据表创建完成")


if __name__ == "__main__":
    asyncio.run(main())
