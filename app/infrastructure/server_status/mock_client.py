# app/infrastructure/server_status/mock_client.py
import asyncio

from app.infrastructure.server_status.base import ServerStatus, ServerStatusClient

_MOCK_STATUS = {
    "192.168.1.100": ServerStatus(ip="192.168.1.100", cpu=92, memory=78, disk=65, status="告警"),
    "192.168.1.101": ServerStatus(ip="192.168.1.101", cpu=35, memory=52, disk=40, status="正常"),
    "192.168.1.102": ServerStatus(ip="192.168.1.102", cpu=15, memory=88, disk=30, status="告警"),
}


class MockServerStatusClient(ServerStatusClient):
    async def get_status(self, ip: str) -> ServerStatus | None:
        await asyncio.sleep(0)  # 保持异步接口形态一致
        return _MOCK_STATUS.get(ip)