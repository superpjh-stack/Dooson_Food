from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.shared.base_model import BaseModel, TimestampMixin


class ProductionLine(Base, TimestampMixin):
    __tablename__ = 'production_lines'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    capacity_per_hour: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), default='EA')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Process(Base, TimestampMixin):
    __tablename__ = 'processes'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sequence: Mapped[int] = mapped_column(nullable=False)
    line_id: Mapped[int | None] = mapped_column(ForeignKey('production_lines.id'), nullable=True)
    standard_duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    is_ccp: Mapped[bool] = mapped_column(Boolean, default=False)


class ProcessRecord(Base, TimestampMixin):
    __tablename__ = 'process_records'

    id: Mapped[int] = mapped_column(primary_key=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey('work_orders.id'), nullable=False)
    process_id: Mapped[int] = mapped_column(ForeignKey('processes.id'), nullable=False)
    lot_id: Mapped[int | None] = mapped_column(ForeignKey('lots.id'), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='PENDING')
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    operator: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class WorkOrder(BaseModel):
    """생산지시 — BOM 버전은 생성 시점에 잠금 (mid-order 변경 불가)."""
    __tablename__ = "work_orders"

    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    # product_id: nullable Int FK placeholder — products table not yet modeled
    product_id: Mapped[int | None] = mapped_column(nullable=True)
    production_line_id: Mapped[int | None] = mapped_column(nullable=True)
    planned_qty: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    actual_qty: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="EA")
    # PLANNED | IN_PROGRESS | COMPLETED | CANCELLED
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PLANNED")
    planned_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    planned_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # BOM version locked at WorkOrder creation time — mid-order BOM changes do not apply
    bom_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
