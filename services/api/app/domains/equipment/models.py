from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.shared.base_model import BaseModel, TimestampMixin


class Equipment(BaseModel):
    """설비 — STERILIZER, XRAY, MIXER, FILLER, SEALER, OTHER."""
    __tablename__ = "equipment"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # STERILIZER | XRAY | MIXER | FILLER | SEALER | OTHER
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    # nullable FK placeholder — production_lines table not yet modeled
    line_id: Mapped[int | None] = mapped_column(nullable=True)
    # RUNNING | IDLE | FAULT | MAINTENANCE
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="IDLE")
    # OEE 0–100 %
    oee: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    last_maintained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class IotSensorReading(Base, TimestampMixin):
    """TimescaleDB hypertable — partitioned by recorded_at."""
    __tablename__ = 'iot_sensor_readings'

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey('equipment.id'), nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    quality: Mapped[str] = mapped_column(String(20), default='GOOD')
