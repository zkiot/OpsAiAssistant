import logging

from pymilvus import DataType, MilvusClient

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: MilvusClient | None = None


def get_milvus_client() -> MilvusClient:
    global _client
    if _client is None:
        _client = MilvusClient(uri=settings.MILVUS_URI)
    return _client


async def init_milvus() -> None:
    """应用启动时调用：确保 collection 存在。真实项目里建议把建表操作放到
    独立的迁移/初始化脚本里（见 scripts/init_db.py），这里仅做存在性检查。
    """
    client = get_milvus_client()
    if client.has_collection(settings.MILVUS_COLLECTION):
        logger.info("Milvus collection '%s' 已存在", settings.MILVUS_COLLECTION)
        return

    schema = client.create_schema(auto_id=True, enable_dynamic_field=True)
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=4096)
    schema.add_field(field_name="category", datatype=DataType.VARCHAR, max_length=64)

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="HNSW",
        metric_type="COSINE",
        params={"M": 16, "efConstruction": 200},
    )

    client.create_collection(
        collection_name=settings.MILVUS_COLLECTION,
        schema=schema,
        index_params=index_params,
    )
    logger.info("Milvus collection '%s' 创建完成", settings.MILVUS_COLLECTION)


async def close_milvus() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
