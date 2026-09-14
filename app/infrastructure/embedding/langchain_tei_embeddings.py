# app/infrastructure/embedding/langchain_tei_embeddings.py
from langchain_core.embeddings import Embeddings

from app.infrastructure.embedding.tei_client import TEIEmbeddingClient


class LangChainTEIEmbeddings(Embeddings):
    """把你自己的 TEIEmbeddingClient 适配成 LangChain 期望的 Embeddings 接口。
    这样 langchain_milvus.Milvus 这类现成组件才能直接使用你本地的 BGE-M3 服务。
    """

    def __init__(self):
        self._client = TEIEmbeddingClient()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        import asyncio
        return asyncio.run(self._client.embed_documents(texts))

    def embed_query(self, text: str) -> list[float]:
        import asyncio
        return asyncio.run(self._client.embed_query(text))