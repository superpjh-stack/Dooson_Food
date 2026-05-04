import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class EquipmentCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    type: str = Field(..., pattern=r"^(STERILIZER|XRAY|MIXER|FILLER|SEALER|OTHER)$")
    line_id: int | None = None
    status: str = Field(default="IDLE", pattern=r"^(RUNNING|IDLE|FAULT|MAINTENANCE)$")
    oee: Decimal | None = Field(None, ge=0, le=100)
    last_maintained_at: datetime | None = None
    notes: str | None = None


class EquipmentUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    type: str | None = Field(None, pattern=r"^(STERILIZER|XRAY|MIXER|FILLER|SEALER|OTHER)$")
    line_id: int | None = None
    oee: Decimal | None = Field(None, ge=0, le=100)
    last_maintained_at: datetime | None = None
    notes: str | None = None


class EquipmentStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(RUNNING|IDLE|FAULT|MAINTENANCE)$")


class EquipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    type: str
    line_id: int | None
    status: str
    oee: Decimal | None
    last_maintained_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime | None


class IotSensorReadingCreate(BaseModel):
    sensor_type: str = Field(..., max_length=50)
    value: float
    unit: str = Field(..., max_length=20)
    recorded_at: datetime
    quality: str = Field(default='GOOD', pattern=r'^(GOOD|BAD|UNCERTAIN)$')


class IotSensorReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment_id: int
    sensor_type: str
    value: Decimal
    unit: str
    recorded_at: datetime
    quality: str
    created_at: datetime
