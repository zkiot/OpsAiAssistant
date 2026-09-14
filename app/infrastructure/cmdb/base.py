# app/infrastructure/cmdb/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AssetInfo:
    asset_id: str
    name: str
    owner: str          # 负责人
    business: str        # 所属业务
    idc: str              # 机房
    status: str = "运行中"


class CMDBClient(ABC):
    @abstractmethod
    async def query_asset(self, keyword: str) -> list[AssetInfo]:
        """按关键词（资产名/IP/资产ID）查询资产信息，可能匹配多条。"""
        ...