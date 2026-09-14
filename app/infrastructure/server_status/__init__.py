# app/infrastructure/server_status/__init__.py
from app.core.config import settings
from app.infrastructure.server_status.base import ServerStatusClient
from app.infrastructure.server_status.http_client import HttpServerStatusClient
from app.infrastructure.server_status.mock_client import MockServerStatusClient


def get_server_status_client() -> ServerStatusClient:
    if settings.MONITOR_USE_MOCK:
        return MockServerStatusClient()
    return HttpServerStatusClient()