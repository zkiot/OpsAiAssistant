# app/infrastructure/mcp/pool.py
import asyncio
import logging
from contextlib import asynccontextmanager

from mcp import Client, StdioServerParameters

logger = logging.getLogger(__name__)


class MCPConnectionPool:
    """维护 N 个常驻的 MCP 连接，避免每次调用都重新起 stdio 子进程。
    用法思路和 Java 里的连接池（HikariCP）一致：启动时预建好连接，
    调用时从池子里借一个、用完还回去。
    """

    def __init__(self, target: str | StdioServerParameters, pool_size: int = 3):
        self._target = target
        self._pool_size = pool_size
        self._queue: asyncio.Queue[Client] = asyncio.Queue()
        self._clients: list[Client] = []
        self._initialized = False

    async def start(self) -> None:
        if self._initialized:
            return
        for i in range(self._pool_size):
            client = Client(self._target)
            await client.__aenter__()  # 手动进入连接的 async context，让它保持常驻
            self._clients.append(client)
            await self._queue.put(client)
        self._initialized = True
        logger.info("MCP 连接池初始化完成，连接数: %d", self._pool_size)

    async def close(self) -> None:
        for client in self._clients:
            try:
                await client.__aexit__(None, None, None)
            except Exception as exc:
                logger.warning("关闭 MCP 连接失败: %s", exc)
        self._clients.clear()
        self._initialized = False

    @asynccontextmanager
    async def acquire(self):
        """从池子里借一个连接，用完自动还回去（哪怕中间抛异常也会归还）。"""
        client = await self._queue.get()
        try:
            yield client
        finally:
            await self._queue.put(client)