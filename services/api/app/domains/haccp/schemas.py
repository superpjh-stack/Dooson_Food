import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HaccpCheckPlanCreate(BaseModel):
    ccp_id: uuid.UUID
    check_frequency: str = Field(..., pattern=r"^(HOURLY|DAILY|PER_LOT|WEEKLY)$")
    check_method: str
    corrective_action: str
    responsible_person: str
    is_active: bool = True


class HaccpCheckPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ccp_id: uuid.UUID
    check_frequency: str
    check_method: str
    corrective_action: str
    responsible_person: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class HaccpCheckRecordCreate(BaseModel):
    plan_id: uuid.UUID
    lot_id: uuid.UUID | None = None
    work_order_id: uuid.UUID | None = None
    # 전자서명: 점검자 username (식약처 요구사항)
    checked_by: str = Field(..., min_length=1, max_length=100)
    checked_at: datetime
    result: str = Field(..., pattern=r"^(PASS|FAIL|CONDITIONAL_PASS)$")
    measured_values: dict = Field(default_factory=dict)
    corrective_action_taken: str | None = None
    notes: str | None = None


class HaccpCheckRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plan_id: uuid.UUID
    lot_id: uuid.UUID | None
    work_order_id: uuid.UUID | None
    checked_by: str
    checked_at: datetime
    result: str
    measured_values: dict
    corrective_action_taken: str | None
    notes: str | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
