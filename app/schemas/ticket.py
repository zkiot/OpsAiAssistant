# app/schemas/ticket.py
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["P1", "P2", "P3", "P4"]


class TicketCreateRequest(BaseModel):
    server_ip: str = Field(..., min_length=1, max_length=64, description="故障服务器IP")
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    severity: Severity = "P3"


class TicketOut(BaseModel):
    """API 返回给前端的工单信息，和 models.Ticket 的 ORM 字段分开管理。"""

    id: str
    server_ip: str
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}  # 允许直接从 ORM 对象转换


class TicketListResponse(BaseModel):
    total: int
    items: list[TicketOut]