import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LotCreate(BaseModel):
    code: str = Field(..., pattern=r"^DS-\d{8}-\w+-\d{4}$", description="DS-YYYYMMDD-제품코드-순번")
    type: str = Field(..., pattern=r"^(RAW|WIP|FG)$")
    product_id: uuid.UUID
    work_order_id: uuid.UUID | None = None
    supplier_id: uuid.UUID | None = None
    qty: Decimal = Field(..., gt=0)
    unit: str
    parent_lot_ids: list[uuid.UUID] = Field(default_factory=list)
    qty_used_per_parent: dict[str, Decimal] = Field(default_factory=dict)
    received_at: datetime | None = None
    produced_at: datetime | None = None
    expiry_date: date | None = None
    storage_location: str | None = None


class LotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    type: str
    product_id: uuid.UUID
    work_order_id: uuid.UUID | None
    qty: Decimal
    unit: str
    status: str
    produced_at: datetime | None
    expiry_date: date | None
    storage_location: str | None
    created_at: datetime


class LotLineageNode(BaseModel):
    lot: LotResponse
    depth: int
    qty_used: Decimal | None = None
    relation_type: str | None = None


class LotTraceResponse(BaseModel):
    target_lot: LotResponse
    ancestors: list[LotLineageNode]
    query_ms: int


class LotForwardTraceResponse(BaseModel):
    source_lot: LotResponse
    affected_fg_lots: list[LotLineageNode]
    query_ms: int


class RecallSimulationRequest(BaseModel):
    raw_lot_id: uuid.UUID
    reason: str | None = None


class RecallSimulationResponse(BaseModel):
    source_lot: LotResponse
    affected_lots: list[LotResponse]
    total_affected: int
    shipped_count: int
    in_stock_count: int
