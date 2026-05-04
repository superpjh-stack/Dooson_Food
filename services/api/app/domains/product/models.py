from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import TimestampMixin
from app.infrastructure.database import Base


class Product(Base, TimestampMixin):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), default='EA')
    shelf_life_days: Mapped[int | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Bom(Base, TimestampMixin):
    __tablename__ = 'boms'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_from: Mapped[datetime] = mapped_column(nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class BomItem(Base, TimestampMixin):
    __tablename__ = 'bom_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    bom_id: Mapped[int] = mapped_column(ForeignKey('boms.id'), nullable=False)
    material_code: Mapped[str] = mapped_column(String(50), nullable=False)
    material_name: Mapped[str] = mapped_column(String(200), nullable=False)
    qty_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
