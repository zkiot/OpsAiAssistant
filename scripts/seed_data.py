"""向知识库灌入一批示例文档，方便本地开发时有数据可查。

用法: python -m scripts.seed_data
"""

import asyncio

from app.services.rag_service import RAGService

SAMPLE_DOCS = [
    "磁盘告警处理流程：先通过 df -h 检查挂载点使用率，确认是否为日志文件堆积导致，"
    "清理或归档旧日志后观察告警是否恢复。",
    "CMDB 资产同步失败常见原因：云厂商 API Key 过期、网络策略变更导致无法访问云厂商接口，"
    "建议先检查同步任务日志定位具体报错。",
]


async def main():
    rag_service = RAGService()
    count = await rag_service.ingest(SAMPLE_DOCS, category="故障处理")
    print(f"已写入 {count} 条示例文档")


if __name__ == "__main__":
    asyncio.run(main())
