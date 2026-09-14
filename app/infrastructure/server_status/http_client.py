# app/infrastructure/server_status/http_client.py
import logging

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import UpstreamServiceError
from app.core.http_client import get_http_client
from app.infrastructure.server_status.base import ServerStatus, ServerStatusClient

logger = logging.getLogger(__name__)


class HttpServerStatusClient(ServerStatusClient):
    """对接真实监控平台的API，字段名按你们实际接口返回结构调整。"""

    def __init__(self, base_url: str | None = None):
        self._base_url = base_url or settings.MONITOR_API_URL

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def get_status(self, ip: str) -> ServerStatus | None:
        client = get_http_client()
        try:
            resp = await client.get(f"{self._base_url}/servers/{ip}/status")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.error("服务器状态查询失败: %s", exc)
            raise UpstreamServiceError("监控系统", str(exc)) from exc

        return ServerStatus(
            ip=ip,
            cpu=data.get("cpu_usage", 0),
            memory=data.get("memory_usage", 0),
            disk=data.get("disk_usage", 0),
            status=data.get("health_status", "未知"),
        )