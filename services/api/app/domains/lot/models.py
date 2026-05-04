import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel, TimestampMixin
from app.infrastructure.database import Base


class Lot(BaseModel):
    __tablename__ = "lots"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # RAW | WIP | FG
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    work_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_orders.id"), nullable=True
    )
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    qty: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    produced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    storage_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    qr_code: Mapped[str | None] = mapped_column(String(200), nullable=True)
    rfid_tag: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # relationships
    lineage_as_ancestor: Mapped[list["LotLineage"]] = relationship(
        "LotLineage", foreign_keys="LotLineage.ancestor_lot_id", back_populates="ancestor"
    )
    lineage_as_descendant: Mapped[list["LotLineage"]] = relationship(
        "LotLineage", foreign_keys="LotLineage.descendant_lot_id", back_populates="descendant"
    )


class LotLineage(Base, TimestampMixin):
    """Closure Table for LOT ancestry — supports O(1) traceability queries."""
    __tablename__ = "lot_lineage"

    ancestor_lot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lots.id"), primary_key=True
    )
    descendant_lot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lots.id"), primary_key=True
    )
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    relation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    qty_used: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

    ancestor: Mapped["Lot"] = relationship("Lot", foreign_keys=[ancestor_lot_id])
    descendant: Mapped["Lot"] = relationship("Lot", foreign_keys=[descendant_lot_id])
