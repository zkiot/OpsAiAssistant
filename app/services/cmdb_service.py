# app/services/cmdb_service.py
from app.infrastructure.cmdb import get_cmdb_client
from app.infrastructure.cmdb.base import AssetInfo, CMDBClient


class CMDBService:
    def __init__(self, cmdb_client: CMDBClient | None = None):
        self._cmdb = cmdb_client or get_cmdb_client()

    async def query_asset(self, keyword: str) -> list[AssetInfo]:
        if not keyword.strip():
            return []
        return await self._cmdb.query_asset(keyword)

    async def query_asset_as_text(self, keyword: str) -> str:
        """给 LLM/MCP 工具用的文本格式化版本。"""
        assets = await self.query_asset(keyword)
        if not assets:
            return f"未查询到与「{keyword}」相关的资产信息"
        lines = [
            f"- {a.name}（{a.asset_id}）：负责人 {a.owner}，所属业务 {a.business}，机房 {a.idc}，状态 {a.status}"
            for a in assets
        ]
        return "\n".join(lines)