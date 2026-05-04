import logging
import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.equipment.models import Equipment, IotSensorReading
from app.domains.equipment.schemas import (
    EquipmentCreate, EquipmentResponse, EquipmentUpdate,
    IotSensorReadingCreate, IotSensorReadingResponse,
)
from app.shared.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class EquipmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: EquipmentCreate) -> EquipmentResponse:
        equip = Equipment(**data.model_dump())
        self.db.add(equip)
        await self.db.flush()
        logger.info(f"[EQUIPMENT] Created: {equip.code} type={equip.type} status={equip.status}")
        return EquipmentResponse.model_validate(equip)

    async def get(self, equipment_id: uuid.UUID) -> EquipmentResponse:
        result = await self.db.execute(select(Equipment).where(Equipment.id == equipment_id))
        equip = result.scalar_one_or_none()
        if equip is None:
            raise NotFoundException(f"설비를 찾을 수 없습니다: {equipment_id}")
        return EquipmentResponse.model_validate(equip)

    async def list_equipment(
        self,
        status: str | None = None,
        type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        stmt = select(Equipment)
        if status is not None:
            stmt = stmt.where(Equipment.status == status)
        if type is not None:
            stmt = stmt.where(Equipment.type == type)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Equipment.code).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        items = [EquipmentResponse.model_validate(e) for e in result.scalars().all()]
        return {"items": items, "total": total, "page": skip // limit + 1, "limit": limit}

    async def update(self, equipment_id: uuid.UUID, data: EquipmentUpdate) -> EquipmentResponse:
        result = await self.db.execute(select(Equipment).where(Equipment.id == equipment_id))
        equip = result.scalar_one_or_none()
        if equip is None:
            raise NotFoundException(f"설비를 찾을 수 없습니다: {equipment_id}")
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(equip, field, value)
        await self.db.flush()
        logger.info(f"[EQUIPMENT] Updated: {equip.code}")
        return EquipmentResponse.model_validate(equip)

    async def update_status(self, equipment_id: uuid.UUID, status: str) -> EquipmentResponse:
        result = await self.db.execute(select(Equipment).where(Equipment.id == equipment_id))
        equip = result.scalar_one_or_none()
        if equip is None:
            raise NotFoundException(f"설비를 찾을 수 없습니다: {equipment_id}")
        previous = equip.status
        equip.status = status
        await self.db.flush()
        if status == "FAULT":
            logger.warning(f"[EQUIPMENT] FAULT detected: {equip.code} {previous}→FAULT")
        else:
            logger.info(f"[EQUIPMENT] Status changed: {equip.code} {previous}→{status}")
        return EquipmentResponse.model_validate(equip)

    # ── IoT Sensor Readings ───────────────────────────────────────────────────

    async def record_sensor_reading(
        self, equipment_id: uuid.UUID, data: IotSensorReadingCreate
    ) -> IotSensorReadingResponse:
        equip_result = await self.db.execute(select(Equipment).where(Equipment.id == equipment_id))
        equip = equip_result.scalar_one_or_none()
        if equip is None:
            raise NotFoundException(f"설비를 찾을 수 없습니다: {equipment_id}")

        if data.sensor_type == "TEMPERATURE" and equip.type == "STERILIZER" and data.value > 125:
            logger.warning(
                f"[IOT] TEMPERATURE threshold exceeded: equip={equip.code} value={data.value}°C"
            )

        reading = IotSensorReading(
            equipment_id=equip.id,
            sensor_type=data.sensor_type,
            value=data.value,
            unit=data.unit,
            recorded_at=data.recorded_at,
            quality=data.quality,
        )
        self.db.add(reading)
        await self.db.flush()
        logger.info(
            f"[IOT] equip={equip.code} sensor={data.sensor_type} value={data.value}{data.unit}"
        )
        return IotSensorReadingResponse.model_validate(reading)

    async def get_latest_readings(
        self, equipment_id: uuid.UUID, limit: int = 100
    ) -> list[IotSensorReadingResponse]:
        equip_result = await self.db.execute(select(Equipment).where(Equipment.id == equipment_id))
        if equip_result.scalar_one_or_none() is None:
            raise NotFoundException(f"설비를 찾을 수 없습니다: {equipment_id}")
        stmt = (
            select(IotSensorReading)
            .where(IotSensorReading.equipment_id == equipment_id)
            .order_by(IotSensorReading.recorded_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return [IotSensorReadingResponse.model_validate(r) for r in result.scalars().all()]

    async def get_readings_range(
        self,
        equipment_id: uuid.UUID,
        sensor_type: str,
        from_dt: datetime,
        to_dt: datetime,
    ) -> list[IotSensorReadingResponse]:
        equip_result = await self.db.execute(select(Equipment).where(Equipment.id == equipment_id))
        if equip_result.scalar_one_or_none() is None:
            raise NotFoundException(f"설비를 찾을 수 없습니다: {equipment_id}")
        stmt = (
            select(IotSensorReading)
            .where(
                IotSensorReading.equipment_id == equipment_id,
                IotSensorReading.sensor_type == sensor_type,
                IotSensorReading.recorded_at >= from_dt,
                IotSensorReading.recorded_at <= to_dt,
            )
            .order_by(IotSensorReading.recorded_at)
        )
        result = await self.db.execute(stmt)
        return [IotSensorReadingResponse.model_validate(r) for r in result.scalars().all()]
