import logging

from app.core.config import settings
from app.infrastructure.embedding.tei_client import TEIEmbeddingClient
from app.infrastructure.vectorstore.milvus_client import get_milvus_client

logger = logging.getLogger(__name__)


class RAGService:
    """负责向量检索这部分逻辑。混合检索（BM25等）可以在这里扩展，
    保持和 chat_service 的业务编排逻辑分开。
    """

    def __init__(self, embedding_client: TEIEmbeddingClient | None = None):
        self._embedding_client = embedding_client or TEIEmbeddingClient()

    async def retrieve(self, question: str, top_k: int = 3) -> list[dict]:
        query_vector = await self._embedding_client.embed_query(question)

        client = get_milvus_client()
        results = client.search(
            collection_name=settings.MILVUS_COLLECTION,
            data=[query_vector],
            limit=top_k,
            output_fields=["text", "category"],
        )
        if not results:
            return []
        return [
            {"text": hit["entity"]["text"], "category": hit["entity"]["category"], "score": hit["distance"]}
            for hit in results[0]
        ]
    async def query(self, question: str, top_k: int = 3) -> dict:
        """对外提供的查询接口，封装了向量检索和后续的业务逻辑处理。"""
        retrieved_docs = await self.retrieve(question, top_k=top_k)
        # 这里可以根据业务需求对检索结果进行进一步处理，比如过滤、排序等
        return {"question": question,
                "answers": str(retrieved_docs)}

    async def ingest(self, texts: list[str], category: str = "未分类") -> int:
        vectors = await self._embedding_client.embed_documents(texts)
        client = get_milvus_client()
        data = [
            {"vector": vectors[i], "text": texts[i], "category": category} for i in range(len(texts))
        ]
        client.insert(collection_name=settings.MILVUS_COLLECTION, data=data)
        return len(data)
