# test_mcp.py
import asyncio
from pathlib import Path

from app.infrastructure.mcp.mcp_client import MCPToolClient, build_stdio_target
from app.infrastructure.mcp.pool import MCPConnectionPool

PROJECT_ROOT = Path(__file__).resolve().parent


async def main():
    target = build_stdio_target(
        command="python",
        args=["-m", "mcp_server.server"],
        cwd=str(PROJECT_ROOT),
    )

    # 关键修复：先建连接池，start()启动之后，再把池子传给 MCPToolClient
    pool = MCPConnectionPool(target, pool_size=1)  # 测试脚本用1个连接就够
    await pool.start()

    try:
        client = MCPToolClient(pool)

        tools = await client.list_tools()
        print("可用工具：", [t["name"] for t in tools])

        result = await client.call_tool("query_cmdb_asset", {"keyword": "ops-web"})
        print("CMDB查询结果：\n", result)

        result = await client.call_tool("create_ticket", {
            "server_ip": "10.0.0.1",
            "title": "磁盘告警",
            "description": "磁盘使用率超过90%",
            "severity": "P2",
        })
        print("工单创建结果：\n", result)
    finally:
        await pool.close()  # 记得关闭，释放子进程


if __name__ == "__main__":
    asyncio.run(main())