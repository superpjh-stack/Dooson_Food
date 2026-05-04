import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    type: str
    severity: str = "INFO"
    title: str
    body: str
    lot_id: uuid.UUID | None = None
    work_order_id: uuid.UUID | None = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    severity: str
    title: str
    body: str
    lot_id: uuid.UUID | None
    work_order_id: uuid.UUID | None
    is_read: bool
    read_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
