import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel, TimestampMixin, SoftDeleteMixin


class HaccpCheckPlan(BaseModel):
    """HACCP 점검 계획 — 각 CCP 별 점검 주기/방법/책임자 정의."""
    __tablename__ = "haccp_check_plans"

    ccp_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ccps.id"), nullable=False
    )
    # HOURLY | DAILY | PER_LOT | WEEKLY
    check_frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    check_method: Mapped[str] = mapped_column(Text, nullable=False)
    corrective_action: Mapped[str] = mapped_column(Text, nullable=False)
    responsible_person: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class HaccpCheckRecord(BaseModel, SoftDeleteMixin):
    """HACCP 점검 기록 — 식약처 규정: 2년 보존 필수, 소프트 삭제만 허용, 전자서명 포함."""
    __tablename__ = "haccp_check_records"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("haccp_check_plans.id"), nullable=False
    )
    lot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lots.id"), nullable=True
    )
    work_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    # 전자서명: 점검자 username
    checked_by: Mapped[str] = mapped_column(String(100), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # PASS | FAIL | CONDITIONAL_PASS
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    # JSONB — measured values dict e.g. {"temperature": 121.5, "pressure": 2.1}
    measured_values: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    corrective_action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
