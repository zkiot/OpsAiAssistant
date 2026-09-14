from datetime import datetime

from pydantic import BaseModel


class DocumentIngestRequest(BaseModel):
    content: str
    category: str = "未分类"


class DocumentOut(BaseModel):
    """API 返回给前端的文档信息，故意和 models.Document 的 ORM 字段分开，
    避免数据库内部字段（比如向量、内部ID）被意外暴露。
    """

    id: int
    category: str
    preview: str
    created_at: datetime

    model_config = {"from_attributes": True}
