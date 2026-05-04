import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base
from app.shared.base_model import BaseModel, TimestampMixin


class Ccp(BaseModel):
    __tablename__ = "ccps"

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # CCP-1 ~ CCP-7
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    process_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    parameter: Mapped[str] = mapped_column(String(50), nullable=False)  # temperature, f_value, ...
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    limit_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    limit_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    monitoring_freq: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    records: Mapped[list["CcpRecord"]] = relationship("CcpRecord", back_populates="ccp")


class CcpRecord(BaseModel):
    __tablename__ = "ccp_records"

    ccp_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ccps.id"), nullable=False
    )
    work_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    lot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lots.id"), nullable=True
    )
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    measured_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    measured_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_deviation: Mapped[bool] = mapped_column(Boolean, default=False)
    corrective_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_urls: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    ccp: Mapped["Ccp"] = relationship("Ccp", back_populates="records")


class FValueRecord(BaseModel):
    __tablename__ = "f_value_records"

    sterilizer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    work_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    lot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lots.id"), nullable=True
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    f0_target: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    f0_calculated: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    is_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ai_prediction: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    ai_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)


class XRayResult(BaseModel):
    __tablename__ = "xray_results"

    machine_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    work_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    lot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lots.id"), nullable=True
    )
    inspected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    result: Mapped[str] = mapped_column(String(5), nullable=False)  # OK | NG
    contaminant_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contaminant_size: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    grad_cam_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ai_classification: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class FValueTemperatureSeries(Base, TimestampMixin):
    """TimescaleDB hypertable — time-series of temperatures during one sterilization run."""
    __tablename__ = 'f_value_temperature_series'

    id: Mapped[int] = mapped_column(primary_key=True)
    f_value_record_id: Mapped[int] = mapped_column(
        ForeignKey('f_value_records.id'), nullable=False
    )
    temperature: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(nullable=False)
