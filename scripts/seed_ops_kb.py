# scripts/seed_ops_kb.py
import asyncio
import re

from app.services.rag_service import RAGService


def split_by_h3(md_text: str) -> list[str]:
    """按三级标题（###）切分，每个小节独立成一个chunk，保留标题作为上下文。"""
    sections = re.split(r"\n(?=### )", md_text)
    return [s.strip() for s in sections if s.strip() and s.strip().startswith("###")]


async def main():
    with open("生产环境常见问题知识库.md", encoding="utf-8") as f:
        content = f.read()

    chunks = split_by_h3(content)
    rag_service = RAGService()
    count = await rag_service.ingest(chunks, category="故障处理规范")
    print(f"已写入 {count} 个知识片段")


if __name__ == "__main__":
    asyncio.run(main())