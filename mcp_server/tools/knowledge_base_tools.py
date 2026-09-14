from mcp.server.mcpserver import MCPServer

from app.services.rag_service import RAGService

mcp = MCPServer("运维知识库")
rag_service = RAGService()  # 直接复用现有的服务，不重复造轮子


@mcp.tool()
async def query_ops_knowledge(question: str) -> str:
    """查询运维知识库，获取故障处理方案和操作规范"""
    results = await rag_service.retrieve(question, top_k=3)
    if not results:
        return "知识库中没有找到相关内容"
    return "\n".join(f"- {r['text']}" for r in results)