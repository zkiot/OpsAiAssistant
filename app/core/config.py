from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py 在 app/core/config.py，往上两级就是项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
class Settings(BaseSettings):
    """全局配置。启动时从 .env / 环境变量加载，类型校验失败会在启动阶段直接报错，
    避免类似 base_url 读成 None 却在运行时才发现的问题。
    """

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    APP_NAME: str = "AI运维助手"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # LLM
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"

    # Embedding
    EMBEDDING_SERVICE_URL: str = "http://127.0.0.1:8001"

    # Milvus
    MILVUS_URI: str = "http://127.0.0.1:19530"
    MILVUS_COLLECTION: str = "ops_knowledge"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    SESSION_TTL_SECONDS: int = 3600

    CMDB_API_URL: str = ""
    CMDB_USE_MOCK: bool = True  # 默认用Mock，接了真实CMDB后改成False

    # app/core/config.py（追加）
    MONITOR_API_URL: str = ""
    MONITOR_USE_MOCK: bool = True


@lru_cache
def get_settings() -> Settings:
    """缓存 Settings 实例，避免每次请求都重新解析环境变量。"""
    return Settings()


settings = get_settings()
