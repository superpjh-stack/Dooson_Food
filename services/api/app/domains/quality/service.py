import uuid
import logging
from datetime import datetime, UTC
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.lot.service import LotService
from app.domains.notification.schemas import NotificationCreate
from app.domains.notification.service import NotificationService
from app.domains.quality.models import Ccp, CcpRecord, FValueRecord, FValueTemperatureSeries, XRayResult
from app.domains.quality.schemas import (
    CcpRecordCreate, FValueRecordCreate, FValueTemperatureCreate,
    FValueTemperatureResponse, XRayResultCreate,
)
from app.shared.exceptions import NotFoundException
from app.config import settings

logger = logging.getLogger(__name__)


def calculate_f0(temp_readings: list[float], delta_t_minutes: float = 1.0) -> float:
    """Bigelow formula: F0 = sum(10^((T - Tref) / z) * delta_t) for each reading.
    Sterilization reference: Tref=121.1°C, z=10°C."""
    tref, z = 121.1, 10.0
    return sum(10 ** ((t - tref) / z) * delta_t_minutes for t in temp_readings)


class QualityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_ccp(self, ccp_id: uuid.UUID) -> Ccp:
        result = await self.db.execute(select(Ccp).where(Ccp.id == ccp_id))
        ccp = result.scalar_one_or_none()
        if not ccp:
            raise NotFoundException("CCP 정의를 찾을 수 없습니다")
        return ccp

    def _check_deviation(self, ccp: Ccp, value: Decimal) -> bool:
        if ccp.limit_min is not None and value < ccp.limit_min:
            return True
        if ccp.limit_max is not None and value > ccp.limit_max:
            return True
        return False

    async def record_ccp(self, payload: CcpRecordCreate) -> CcpRecord:
        ccp = await self._get_ccp(payload.ccp_id)
        is_deviation = self._check_deviation(ccp, payload.measured_value)

        record = CcpRecord(
            ccp_id=payload.ccp_id,
            work_order_id=payload.work_order_id,
            lot_id=payload.lot_id,
            measured_at=payload.measured_at,
            measured_value=payload.measured_value,
            is_deviation=is_deviation,
            photo_urls=payload.photo_urls,
        )
        self.db.add(record)
        await self.db.flush()

        status = "이탈" if is_deviation else "합격"
        logger.info(
            f"[QUALITY] CCP_RECORD ccp={ccp.code} value={payload.measured_value}{ccp.unit} "
            f"limit=[{ccp.limit_min}, {ccp.limit_max}] deviation={is_deviation} status={status}"
        )

        if is_deviation:
            await self._handle_ccp_deviation(record, ccp, payload)

        return record

    async def _handle_ccp_deviation(
        self, record: CcpRecord, ccp: Ccp, payload: CcpRecordCreate
    ) -> None:
        logger.warning(
            f"[QUALITY] CCP_DEVIATION DETECTED ccp={ccp.code} lot_id={payload.lot_id} "
            f"value={payload.measured_value} → AUTO_HOLD_LOT + CRITICAL_ALERT"
        )
        if payload.lot_id:
            lot_service = LotService(self.db)
            await lot_service.hold(
                payload.lot_id,
                reason=f"CCP 이탈 자동 보류: {ccp.code} {payload.measured_value}{ccp.unit}",
            )

        notification_service = NotificationService(self.db)
        await notification_service.create(NotificationCreate(
            type="CCP_DEVIATION",
            severity="CRITICAL",
            title=f"CCP 이탈 감지: {ccp.code}",
            body=f"측정값 {payload.measured_value}{ccp.unit} — 허용 범위 [{ccp.limit_min}, {ccp.limit_max}]",
            lot_id=payload.lot_id,
            work_order_id=payload.work_order_id,
        ))

    async def list_ccp_records(
        self,
        lot_id: uuid.UUID | None = None,
        work_order_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        from sqlalchemy import func as sa_func
        stmt = select(CcpRecord)
        if lot_id is not None:
            stmt = stmt.where(CcpRecord.lot_id == lot_id)
        if work_order_id is not None:
            stmt = stmt.where(CcpRecord.work_order_id == work_order_id)
        count_stmt = select(sa_func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(CcpRecord.measured_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        from app.domains.quality.schemas import CcpRecordResponse
        items = [CcpRecordResponse.model_validate(r) for r in result.scalars().all()]
        return {"items": items, "total": total, "page": skip // limit + 1, "limit": limit}

    async def list_ccps(self) -> list[Ccp]:
        result = await self.db.execute(select(Ccp).where(Ccp.is_active.is_(True)).order_by(Ccp.code))
        return list(result.scalars().all())

    async def create_f_value_record(self, payload: FValueRecordCreate) -> FValueRecord:
        f0_calculated = None
        is_passed = None

        if payload.temperature_readings:
            f0_calculated = calculate_f0(payload.temperature_readings)
            f0_target = float(payload.f0_target) if payload.f0_target else 10.0
            is_passed = f0_calculated >= f0_target
            logger.info(
                f"[QUALITY] F0={f0_calculated:.2f} target={f0_target} passed={is_passed}"
            )

        record = FValueRecord(
            sterilizer_id=payload.sterilizer_id,
            work_order_id=payload.work_order_id,
            lot_id=payload.lot_id,
            start_time=payload.start_time,
            end_time=datetime.now(UTC),
            f0_target=payload.f0_target,
            f0_calculated=Decimal(str(round(f0_calculated, 4))) if f0_calculated is not None else None,
            is_passed=is_passed,
        )
        self.db.add(record)
        await self.db.flush()
        logger.info(
            f"[QUALITY] F_VALUE_RECORD sterilizer={payload.sterilizer_id} "
            f"target={payload.f0_target}min lot={payload.lot_id}"
        )

        if is_passed is False and payload.lot_id:
            lot_service = LotService(self.db)
            await lot_service.hold(payload.lot_id, reason="FVALUE_FAIL", held_by="system")

            notification_service = NotificationService(self.db)
            await notification_service.create(NotificationCreate(
                type="FVALUE_FAIL",
                severity="CRITICAL",
                title="F값 미달",
                body=f"F0={f0_calculated:.2f}min (목표: {payload.f0_target}min) — LOT 자동 보류",
                lot_id=payload.lot_id,
                work_order_id=payload.work_order_id,
            ))

        return record

    async def record_xray_result(self, payload: XRayResultCreate) -> XRayResult:
        if payload.confidence is not None and payload.confidence < settings.ml_confidence_threshold:
            logger.warning(
                f"[QUALITY] XRAY LOW_CONFIDENCE confidence={payload.confidence} "
                f"threshold={settings.ml_confidence_threshold} → requiring manual review"
            )

        record = XRayResult(**payload.model_dump())
        self.db.add(record)
        await self.db.flush()

        logger.info(
            f"[QUALITY] XRAY_RESULT result={payload.result} "
            f"confidence={payload.confidence} contaminant={payload.contaminant_type} "
            f"lot={payload.lot_id}"
        )

        if payload.result == "NG" and payload.lot_id:
            lot_service = LotService(self.db)
            await lot_service.hold(
                payload.lot_id,
                reason=f"X-Ray NG 자동 보류: {payload.contaminant_type} {payload.contaminant_size}mm",
            )
            logger.warning(f"[QUALITY] XRAY_NG_AUTO_HOLD lot={payload.lot_id}")

            notification_service = NotificationService(self.db)
            await notification_service.create(NotificationCreate(
                type="XRAY_NG",
                severity="CRITICAL",
                title="X-Ray NG 검출",
                body=(
                    f"이물 {payload.contaminant_type} {payload.contaminant_size}mm 검출. "
                    f"confidence={payload.confidence}. LOT 자동 보류 처리됨."
                ),
                lot_id=payload.lot_id,
                work_order_id=payload.work_order_id,
            ))

        return record

    async def append_f_value_temperature(
        self, f_value_record_id: int, data: FValueTemperatureCreate
    ) -> FValueTemperatureResponse:
        record_result = await self.db.execute(
            select(FValueRecord).where(FValueRecord.id == f_value_record_id)
        )
        if record_result.scalar_one_or_none() is None:
            from app.shared.exceptions import NotFoundException
            raise NotFoundException(f"F값 기록을 찾을 수 없습니다: {f_value_record_id}")
        ts = FValueTemperatureSeries(
            f_value_record_id=f_value_record_id,
            temperature=data.temperature,
            recorded_at=data.recorded_at,
            sequence=data.sequence,
        )
        self.db.add(ts)
        await self.db.flush()
        logger.info(
            f"[QUALITY] F_VALUE_TEMP appended: record_id={f_value_record_id} "
            f"seq={data.sequence} temp={data.temperature}°C"
        )
        return FValueTemperatureResponse.model_validate(ts)

    async def list_f_value_temperatures(
        self, f_value_record_id: int
    ) -> list[FValueTemperatureResponse]:
        result = await self.db.execute(
            select(FValueTemperatureSeries)
            .where(FValueTemperatureSeries.f_value_record_id == f_value_record_id)
            .order_by(FValueTemperatureSeries.sequence)
        )
        return [FValueTemperatureResponse.model_validate(r) for r in result.scalars().all()]

    async def list_xray_results(
        self,
        lot_id: uuid.UUID | None = None,
        result_filter: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        from sqlalchemy import func as sa_func
        stmt = select(XRayResult)
        if lot_id is not None:
            stmt = stmt.where(XRayResult.lot_id == lot_id)
        if result_filter is not None:
            stmt = stmt.where(XRayResult.result == result_filter)
        count_stmt = select(sa_func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(XRayResult.inspected_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        from app.domains.quality.schemas import XRayResultResponse
        items = [XRayResultResponse.model_validate(r) for r in result.scalars().all()]
        return {"items": items, "total": total, "page": skip // limit + 1, "limit": limit}
