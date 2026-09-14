from mcp_server.tools.knowledge_base_tools import mcp
# 下面两行必须保留（哪怕IDE提示"未使用"）：import 是为了触发 @mcp.tool() 装饰器执行注册
#
from mcp_server.tools import knowledge_base_tools  # noqa: F401
from mcp_server.tools import ops_tools  # noqa: F401

if __name__ == "__main__":
    mcp.run()  # 默认 stdio，部署到远程时改成 mcp.run(transport="streamable-http")