# app/infrastructure/server_status/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ServerStatus:
    ip: str
    cpu: int          # CPU使用率(%)
    memory: int        # 内存使用率(%)
    disk: int           # 磁盘使用率(%)
    status: str          # 正常/告警


class ServerStatusClient(ABC):
    @abstractmethod
    async def get_status(self, ip: str) -> ServerStatus | None:
        """查询单台服务器状态，查不到返回 None。"""
        ...