import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """业务异常基类，携带 HTTP 状态码和给前端看的 message。"""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code


class KnowledgeBaseNotReadyError(AppException):
    def __init__(self):
        super().__init__("知识库尚未初始化完成，请稍后重试", status.HTTP_503_SERVICE_UNAVAILABLE)


class UpstreamServiceError(AppException):
    """调用 LLM / embedding / 向量库等外部依赖失败时抛出。"""

    def __init__(self, service: str, detail: str):
        super().__init__(f"{service} 调用失败: {detail}", status.HTTP_502_BAD_GATEWAY)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("未捕获的异常: %s %s", request.method, request.url)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "服务器内部错误"},
        )
