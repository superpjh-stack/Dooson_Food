import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"

    type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # CCP_DEVIATION | XRAY_NG | FVALUE_FAIL | EQUIPMENT_FAULT | LOT_HOLD | SYSTEM
    severity: Mapped[str] = mapped_column(
        String(10), nullable=False, default="INFO"
    )  # CRITICAL | WARNING | INFO
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    lot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lots.id", ondelete="SET NULL"), nullable=True
    )
    work_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True
    )
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    read_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
