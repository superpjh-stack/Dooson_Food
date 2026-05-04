from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    category: str | None = Field(None, max_length=100)
    unit: str = Field(default='EA', max_length=20)
    shelf_life_days: int | None = Field(None, ge=1)
    is_active: bool = True
    notes: str | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    category: str | None
    unit: str
    shelf_life_days: int | None
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime | None


class BomCreate(BaseModel):
    product_id: int
    version: str = Field(..., max_length=20)
    is_active: bool = True
    effective_from: datetime
    effective_to: datetime | None = None
    notes: str | None = None


class BomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    version: str
    is_active: bool
    effective_from: datetime
    effective_to: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime | None
    items_count: int = 0


class BomItemCreate(BaseModel):
    bom_id: int
    material_code: str = Field(..., max_length=50)
    material_name: str = Field(..., max_length=200)
    qty_per_unit: Decimal = Field(..., gt=0)
    unit: str = Field(..., max_length=20)
    is_critical: bool = False


class BomItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bom_id: int
    material_code: str
    material_name: str
    qty_per_unit: Decimal
    unit: str
    is_critical: bool
    created_at: datetime
    updated_at: datetime | None


class BomDetailResponse(BomResponse):
    items: list[BomItemResponse] = []
