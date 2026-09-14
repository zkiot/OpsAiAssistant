# app/core/mcp_pool.py（新建）
from pathlib import Path

from app.infrastructure.mcp.mcp_client import build_stdio_target
from app.infrastructure.mcp.pool import MCPConnectionPool

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

mcp_pool = MCPConnectionPool(
    target=build_stdio_target(
        command="python",
        args=["-m", "mcp_server.server"],
        cwd=str(PROJECT_ROOT),
    ),
    pool_size=3,
)