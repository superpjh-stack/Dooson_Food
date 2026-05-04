import uuid
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.equipment.schemas import (
    EquipmentCreate, EquipmentResponse, EquipmentStatusUpdate, EquipmentUpdate,
    IotSensorReadingCreate, IotSensorReadingResponse,
)
from app.domains.equipment.service import EquipmentService
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/equipment", tags=["설비관리"])


def get_equipment_service(db: AsyncSession = Depends(get_db)) -> EquipmentService:
    return EquipmentService(db)


@router.get("")
async def list_equipment(
    status: str | None = Query(None, description="RUNNING | IDLE | FAULT | MAINTENANCE"),
    type: str | None = Query(None, description="STERILIZER | XRAY | MIXER | FILLER | SEALER | OTHER"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: EquipmentService = Depends(get_equipment_service),
):
    logger.info(f"[API] GET /equipment status={status} type={type} skip={skip} limit={limit}")
    return await service.list_equipment(status=status, type=type, skip=skip, limit=limit)


@router.post("", response_model=EquipmentResponse, status_code=201)
async def create_equipment(
    payload: EquipmentCreate,
    service: EquipmentService = Depends(get_equipment_service),
):
    logger.info(f"[API] POST /equipment code={payload.code}")
    return await service.create(payload)


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: uuid.UUID,
    service: EquipmentService = Depends(get_equipment_service),
):
    logger.info(f"[API] GET /equipment/{equipment_id}")
    return await service.get(equipment_id)


@router.patch("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: uuid.UUID,
    payload: EquipmentUpdate,
    service: EquipmentService = Depends(get_equipment_service),
):
    logger.info(f"[API] PATCH /equipment/{equipment_id}")
    return await service.update(equipment_id, payload)


@router.patch("/{equipment_id}/status", response_model=EquipmentResponse)
async def update_equipment_status(
    equipment_id: uuid.UUID,
    payload: EquipmentStatusUpdate,
    service: EquipmentService = Depends(get_equipment_service),
):
    logger.info(f"[API] PATCH /equipment/{equipment_id}/status status={payload.status}")
    return await service.update_status(equipment_id, payload.status)


# ── IoT Sensor Readings ───────────────────────────────────────────────────────

@router.post(
    "/{equipment_id}/sensors",
    response_model=IotSensorReadingResponse,
    status_code=201,
    tags=["IoT 센서"],
)
async def record_sensor_reading(
    equipment_id: uuid.UUID,
    payload: IotSensorReadingCreate,
    service: EquipmentService = Depends(get_equipment_service),
):
    logger.info(
        f"[API] POST /equipment/{equipment_id}/sensors sensor_type={payload.sensor_type}"
    )
    return await service.record_sensor_reading(equipment_id, payload)


@router.get(
    "/{equipment_id}/sensors/latest",
    response_model=list[IotSensorReadingResponse],
    tags=["IoT 센서"],
)
async def get_latest_readings(
    equipment_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=1000),
    service: EquipmentService = Depends(get_equipment_service),
):
    logger.info(f"[API] GET /equipment/{equipment_id}/sensors/latest limit={limit}")
    return await service.get_latest_readings(equipment_id, limit=limit)


@router.get(
    "/{equipment_id}/sensors/range",
    response_model=list[IotSensorReadingResponse],
    tags=["IoT 센서"],
)
async def get_readings_range(
    equipment_id: uuid.UUID,
    sensor_type: str = Query(...),
    from_dt: datetime = Query(...),
    to_dt: datetime = Query(...),
    service: EquipmentService = Depends(get_equipment_service),
):
    logger.info(
        f"[API] GET /equipment/{equipment_id}/sensors/range "
        f"sensor_type={sensor_type} from={from_dt} to={to_dt}"
    )
    return await service.get_readings_range(equipment_id, sensor_type, from_dt, to_dt)
