# app/core/http_client.py（新建）
import httpx

_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=5.0),   # 连接超时和总超时分开设置
            limits=httpx.Limits(
                max_connections=100,       # 整个应用最多同时维持的连接数
                max_keepalive_connections=20,  # 保持长连接、可复用的连接数
            ),
        )
    return _client


async def close_http_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None