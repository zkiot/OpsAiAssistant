import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.infrastructure.vectorstore.milvus_client import close_milvus, init_milvus
from app.core.mcp_pool import mcp_pool
from app.core.http_client import close_http_client, get_http_client


setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_http_client()  # 初始化全局 httpx.AsyncClient
    # 启动时：初始化外部依赖（向量库连接、建表等）
    logger.info("正在初始化 Milvus 连接...")
    await init_milvus()
    logger.info("正在初始化 MCP 连接池...")
    await mcp_pool.start()
    yield
    close_http_client()  # 关闭全局 httpx.AsyncClient
    # 关闭时：优雅释放资源
    logger.info("正在关闭连接...")
    await close_milvus()
    await mcp_pool.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
