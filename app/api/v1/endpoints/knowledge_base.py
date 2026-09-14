from fastapi import APIRouter, Depends

from app.api.deps import get_rag_service
from app.schemas.knowledge_base import DocumentIngestRequest
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/knowledge-base/ingest")
async def ingest_document(
    request: DocumentIngestRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> dict:
    """向知识库写入一条文档（真实场景通常是批量导入，这里给单条示例）。"""
    count = await rag_service.ingest([request.content], category=request.category)
    return {"ingested": count}

@router.get("/knowledge/query")
async def query_knowledge_base(
    question: str,
    rag_service: RAGService = Depends(get_rag_service),
) -> dict:
    """查询知识库，返回相关文档和答案。"""
    result = await rag_service.query(question)
    return result
