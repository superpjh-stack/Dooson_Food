import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CcpResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    parameter: str
    unit: str
    limit_min: Decimal | None
    limit_max: Decimal | None
    monitoring_freq: str | None
    is_active: bool


class CcpRecordCreate(BaseModel):
    ccp_id: uuid.UUID
    work_order_id: uuid.UUID
    lot_id: uuid.UUID | None = None
    measured_at: datetime
    measured_value: Decimal
    photo_urls: list[str] | None = None


class CcpRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ccp_id: uuid.UUID
    work_order_id: uuid.UUID
    lot_id: uuid.UUID | None
    measured_at: datetime
    measured_value: Decimal
    is_deviation: bool
    corrective_action: str | None
    created_at: datetime


class FValueRecordCreate(BaseModel):
    sterilizer_id: uuid.UUID
    work_order_id: uuid.UUID
    lot_id: uuid.UUID | None = None
    start_time: datetime
    f0_target: Decimal = Field(default=Decimal("10.0"), description="목표 F값 (분)")
    temperature_readings: list[float] = Field(default_factory=list, description="온도 측정값 목록 (°C)")


class FValueRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sterilizer_id: uuid.UUID
    work_order_id: uuid.UUID
    lot_id: uuid.UUID | None
    start_time: datetime
    end_time: datetime | None
    f0_target: Decimal | None
    f0_calculated: Decimal | None
    is_passed: bool | None
    ai_prediction: Decimal | None
    ai_confidence: Decimal | None
    created_at: datetime


class XRayResultCreate(BaseModel):
    machine_id: uuid.UUID
    work_order_id: uuid.UUID
    lot_id: uuid.UUID | None = None
    inspected_at: datetime
    result: str = Field(..., pattern=r"^(OK|NG)$")
    contaminant_type: str | None = None
    contaminant_size: Decimal | None = None
    confidence: Decimal | None = Field(None, ge=0, le=1)
    image_url: str | None = None
    grad_cam_url: str | None = None
    ai_classification: str | None = None

    @model_validator(mode="after")
    def check_ng_requires_confidence(self):
        if self.result == "NG" and self.confidence is None:
            raise ValueError("NG 판정 시 AI confidence 값이 필요합니다")
        return self


class XRayResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    machine_id: uuid.UUID
    work_order_id: uuid.UUID
    lot_id: uuid.UUID | None
    inspected_at: datetime
    result: str
    contaminant_type: str | None
    contaminant_size: Decimal | None
    confidence: Decimal | None
    image_url: str | None
    grad_cam_url: str | None
    ai_classification: str | None
    created_at: datetime


class FValueTemperatureCreate(BaseModel):
    temperature: Decimal = Field(..., description="온도 (°C)")
    recorded_at: datetime
    sequence: int = Field(..., ge=1)


class FValueTemperatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    f_value_record_id: int
    temperature: Decimal
    recorded_at: datetime
    sequence: int
    created_at: datetime
