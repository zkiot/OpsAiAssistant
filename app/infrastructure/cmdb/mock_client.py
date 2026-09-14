# app/infrastructure/cmdb/mock_client.py
import asyncio

from app.infrastructure.cmdb.base import AssetInfo, CMDBClient

_MOCK_ASSETS = [
    AssetInfo(asset_id="SRV-1001", name="ops-web-01", owner="张伟", business="运维平台", idc="上海一号机房"),
    AssetInfo(asset_id="SRV-1002", name="ops-db-01", owner="李娜", business="运维平台", idc="上海一号机房"),
    AssetInfo(asset_id="SRV-2001", name="finance-app-01", owner="王芳", business="财务结算系统", idc="北京二号机房"),
]


class MockCMDBClient(CMDBClient):
    """本地开发/演示用，不用真实 CMDB 接口，按名称模糊匹配示例数据。"""

    async def query_asset(self, keyword: str) -> list[AssetInfo]:
        await asyncio.sleep(0)  # 保持异步接口形态一致
        keyword_lower = keyword.lower()
        return [
            a for a in _MOCK_ASSETS
            if keyword_lower in a.name.lower() or keyword_lower in a.asset_id.lower()
        ]