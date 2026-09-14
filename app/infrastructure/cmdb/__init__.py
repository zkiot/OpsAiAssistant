# app/infrastructure/cmdb/__init__.py
from app.core.config import settings
from app.infrastructure.cmdb.base import CMDBClient
from app.infrastructure.cmdb.http_client import HttpCMDBClient
from app.infrastructure.cmdb.mock_client import MockCMDBClient


def get_cmdb_client() -> CMDBClient:
    if settings.CMDB_USE_MOCK:
        return MockCMDBClient()
    return HttpCMDBClient()