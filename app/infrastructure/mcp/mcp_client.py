# app/infrastructure/mcp/mcp_client.py（改造版）
import logging
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.exceptions import UpstreamServiceError
from app.infrastructure.mcp.pool import MCPConnectionPool,StdioServerParameters
logger = logging.getLogger(__name__)


class MCPToolClient:
    def __init__(self, pool: MCPConnectionPool):
        self._pool = pool

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def list_tools(self) -> list[dict[str, Any]]:
        try:
            async with self._pool.acquire() as client:
                tools = await client.list_tools()
                return [
                    {"name": t.name, "description": t.description, "input_schema": t.input_schema}
                    for t in tools.tools
                ]
        except Exception as exc:
            logger.error("MCP list_tools 失败: %s", exc)
            raise UpstreamServiceError("MCP Server", str(exc)) from exc

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        try:
            async with self._pool.acquire() as client:
                result = await client.call_tool(name, arguments)
                if result.is_error:
                    raise UpstreamServiceError("MCP Server", f"工具 {name} 执行失败: {result.content}")
                return result.content[0].text if result.content else ""
        except UpstreamServiceError:
            raise
        except Exception as exc:
            logger.error("MCP call_tool(%s) 失败: %s", name, exc)
            raise UpstreamServiceError("MCP Server", str(exc)) from exc

# app/infrastructure/mcp/mcp_client.py（追加这个函数）
def mcp_tools_to_openai_schema(mcp_tools: list[dict]) -> list[dict]:
    """把 MCP list_tools() 返回的格式，转换成 DeepSeek/OpenAI 兼容的 Function Calling schema。"""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in mcp_tools
    ]

# app/infrastructure/mcp/mcp_client.py
def build_stdio_target(
    command: str, args: list[str], env: dict[str, str] | None = None, cwd: str | None = None
) -> StdioServerParameters:
    return StdioServerParameters(command=command, args=args, env=env or {}, cwd=cwd)