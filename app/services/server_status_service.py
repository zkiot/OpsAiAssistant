# app/services/server_status_service.py
from app.infrastructure.server_status import get_server_status_client
from app.infrastructure.server_status.base import ServerStatus, ServerStatusClient

# 告警阈值，超过就在文本描述里特别提示
ALERT_THRESHOLDS = {"cpu": 85, "memory": 85, "disk": 85}


class ServerStatusService:
    def __init__(self, client: ServerStatusClient | None = None):
        self._client = client or get_server_status_client()

    async def get_status(self, ip: str) -> ServerStatus | None:
        return await self._client.get_status(ip)

    async def get_status_as_text(self, ip: str) -> str:
        """给 LLM/MCP 工具用的文本格式化版本，超阈值的指标会特别标注出来。"""
        status = await self.get_status(ip)
        if status is None:
            return f"未查询到服务器 {ip} 的状态信息，请确认IP是否正确"

        issues = []
        if status.cpu >= ALERT_THRESHOLDS["cpu"]:
            issues.append(f"CPU使用率过高({status.cpu}%)")
        if status.memory >= ALERT_THRESHOLDS["memory"]:
            issues.append(f"内存使用率过高({status.memory}%)")
        if status.disk >= ALERT_THRESHOLDS["disk"]:
            issues.append(f"磁盘使用率过高({status.disk}%)")

        summary = (
            f"服务器 {status.ip} 当前状态：{status.status}\n"
            f"CPU {status.cpu}% / 内存 {status.memory}% / 磁盘 {status.disk}%"
        )
        if issues:
            summary += f"\n⚠ 异常指标：{'；'.join(issues)}"
        return summary