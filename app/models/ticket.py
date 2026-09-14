# app/models/ticket.py
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    server_ip: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(16), default="P3")   # P1/P2/P3 之类的严重级别
    status: Mapped[str] = mapped_column(String(16), default="待处理")  # 待处理/处理中/已解决
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())