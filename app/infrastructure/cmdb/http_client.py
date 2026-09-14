# app/infrastructure/cmdb/http_client.py
import logging

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import UpstreamServiceError
from app.infrastructure.cmdb.base import AssetInfo, CMDBClient
from app.core.http_client import get_http_client

logger = logging.getLogger(__name__)


class HttpCMDBClient(CMDBClient):
    """对接真实 CMDB 平台的 REST API。字段名按你们实际接口返回结构调整。"""

    def __init__(self, base_url: str | None = None, timeout: int = 15):
        self._base_url = base_url or settings.CMDB_API_URL

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def query_asset(self, keyword: str) -> list[AssetInfo]:
        client = get_http_client()   # 改动：不再自己 async with 新建，用共享实例
        try:
            resp = await client.get(f"{self._base_url}/assets/search", params={"keyword": keyword})
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
                logger.error("CMDB 查询失败: %s", exc)
                raise UpstreamServiceError("CMDB", str(exc)) from exc

        # 按你们CMDB实际返回字段名调整这里的映射
        return [
            AssetInfo(
                asset_id=item["id"],
                name=item["name"],
                owner=item.get("owner", "未知"),
                business=item.get("business_line", "未知"),
                idc=item.get("idc_name", "未知"),
                status=item.get("status", "未知"),
            )
            for item in data.get("items", [])
        ]