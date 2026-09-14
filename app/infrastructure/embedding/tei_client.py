import logging

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import UpstreamServiceError
from app.core.http_client import get_http_client

logger = logging.getLogger(__name__)

BATCH_SIZE = 32  # 与 TEI 启动参数 max_client_batch_size 保持一致


class TEIEmbeddingClient:
    """调用本地 TEI (BGE-M3) 服务的 embedding 客户端。"""

    def __init__(self, base_url: str | None = None):
        self._base_url = base_url or settings.EMBEDDING_SERVICE_URL

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _call(self, texts: list[str]) -> list[list[float]]:
        client = get_http_client()   # 改动：不再自己 async with 新建，用共享实例
        try:
            resp = await client.post(f"{self._base_url}/embed", json={"inputs": texts})
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.error("Embedding 服务调用失败: %s", exc)
            raise UpstreamServiceError("Embedding服务", str(exc)) from exc

    async def embed_query(self, text: str) -> list[float]:
        return (await self._call([text]))[0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]
            results.extend(await self._call(batch))
        return results
