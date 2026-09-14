import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    # 第三方库默认日志级别调高，避免刷屏
    logging.getLogger("httpx").setLevel(logging.WARNING)
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
