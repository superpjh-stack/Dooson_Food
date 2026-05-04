import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductionLineCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    capacity_per_hour: Decimal | None = Field(None, gt=0)
    unit: str = Field(default='EA', max_length=20)
    is_active: bool = True


class ProductionLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    capacity_per_hour: Decimal | None
    unit: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class ProcessCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    sequence: int = Field(..., ge=1)
    line_id: int | None = None
    standard_duration_minutes: int | None = Field(None, ge=1)
    is_ccp: bool = False


class ProcessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    sequence: int
    line_id: int | None
    standard_duration_minutes: int | None
    is_ccp: bool
    created_at: datetime
    updated_at: datetime | None


class ProcessRecordCreate(BaseModel):
    work_order_id: int
    process_id: int
    lot_id: int | None = None
    operator: str | None = None
    notes: str | None = None


class ProcessRecordUpdate(BaseModel):
    status: str | None = Field(None, pattern=r'^(PENDING|IN_PROGRESS|COMPLETED|SKIPPED)$')
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class ProcessRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    work_order_id: int
    process_id: int
    lot_id: int | None
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    operator: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime | None


class WorkOrderCreate(BaseModel):
    code: str | None = Field(None, description="미입력 시 자동 생성: WO-YYYYMMDD-0001")
    product_id: int | None = None
    production_line_id: int | None = None
    planned_qty: Decimal = Field(..., gt=0)
    unit: str = Field(default="EA", max_length=20)
    planned_start: datetime
    planned_end: datetime
    bom_version: str | None = None
    notes: str | None = None


class WorkOrderUpdate(BaseModel):
    status: str | None = Field(None, pattern=r"^(PLANNED|IN_PROGRESS|COMPLETED|CANCELLED)$")
    actual_qty: Decimal | None = Field(None, ge=0)
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    notes: str | None = None


class WorkOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    product_id: int | None
    production_line_id: int | None
    planned_qty: Decimal
    actual_qty: Decimal
    unit: str
    status: str
    planned_start: datetime
    planned_end: datetime
    actual_start: datetime | None
    actual_end: datetime | None
    bom_version: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime | None


class WorkOrderListResponse(BaseModel):
    items: list[WorkOrderResponse]
    total: int
