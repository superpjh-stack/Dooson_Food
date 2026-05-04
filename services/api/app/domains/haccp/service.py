import logging
import uuid
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.haccp.models import HaccpCheckPlan, HaccpCheckRecord
from app.domains.haccp.schemas import (
    HaccpCheckPlanCreate, HaccpCheckPlanResponse,
    HaccpCheckRecordCreate, HaccpCheckRecordResponse,
)
from app.domains.lot.service import LotService
from app.shared.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class HaccpService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Check Plans ──────────────────────────────────────────────────────────

    async def create_check_plan(self, data: HaccpCheckPlanCreate) -> HaccpCheckPlanResponse:
        plan = HaccpCheckPlan(**data.model_dump())
        self.db.add(plan)
        await self.db.flush()
        logger.info(f"[HACCP] CheckPlan created: id={plan.id} ccp={plan.ccp_id} freq={plan.check_frequency}")
        return HaccpCheckPlanResponse.model_validate(plan)

    async def list_check_plans(
        self, is_active: bool | None = None
    ) -> list[HaccpCheckPlanResponse]:
        stmt = select(HaccpCheckPlan)
        if is_active is not None:
            stmt = stmt.where(HaccpCheckPlan.is_active.is_(is_active))
        stmt = stmt.order_by(HaccpCheckPlan.created_at.desc())
        result = await self.db.execute(stmt)
        return [HaccpCheckPlanResponse.model_validate(p) for p in result.scalars().all()]

    # ── Check Records ─────────────────────────────────────────────────────────

    async def create_check_record(
        self, data: HaccpCheckRecordCreate
    ) -> HaccpCheckRecordResponse:
        now = datetime.now(UTC)
        record = HaccpCheckRecord(
            plan_id=data.plan_id,
            lot_id=data.lot_id,
            work_order_id=data.work_order_id,
            checked_by=data.checked_by,
            checked_at=data.checked_at,
            result=data.result,
            measured_values=data.measured_values,
            corrective_action_taken=data.corrective_action_taken,
            notes=data.notes,
        )
        self.db.add(record)
        await self.db.flush()

        # 전자서명 로그 (식약처 감사 추적)
        logger.info(
            f"[HACCP] Record created. checked_by={data.checked_by} "
            f"result={data.result} signed_at={now.isoformat()}"
        )

        if data.result == "FAIL" and data.lot_id:
            lot_service = LotService(self.db)
            await lot_service.hold(
                data.lot_id,
                reason="HACCP_FAIL",
                held_by=data.checked_by,
            )
            logger.warning(
                f"[HACCP] FAIL → LOT auto-held lot_id={data.lot_id} checked_by={data.checked_by}"
            )

        return HaccpCheckRecordResponse.model_validate(record)

    async def list_check_records(
        self,
        plan_id: uuid.UUID | None = None,
        lot_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[HaccpCheckRecordResponse]:
        stmt = select(HaccpCheckRecord).where(HaccpCheckRecord.deleted_at.is_(None))
        if plan_id is not None:
            stmt = stmt.where(HaccpCheckRecord.plan_id == plan_id)
        if lot_id is not None:
            stmt = stmt.where(HaccpCheckRecord.lot_id == lot_id)
        stmt = stmt.order_by(HaccpCheckRecord.checked_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return [HaccpCheckRecordResponse.model_validate(r) for r in result.scalars().all()]

    async def get_check_record(self, record_id: uuid.UUID) -> HaccpCheckRecordResponse:
        result = await self.db.execute(
            select(HaccpCheckRecord).where(HaccpCheckRecord.id == record_id)
        )
        record = result.scalar_one_or_none()
        if record is None:
            raise NotFoundException(f"HACCP 점검 기록을 찾을 수 없습니다: {record_id}")
        return HaccpCheckRecordResponse.model_validate(record)

    async def soft_delete_record(self, record_id: uuid.UUID, deleted_by: str) -> None:
        """소프트 삭제만 허용 — 식약처 규정: HACCP 기록 하드 삭제 금지."""
        result = await self.db.execute(
            select(HaccpCheckRecord).where(HaccpCheckRecord.id == record_id)
        )
        record = result.scalar_one_or_none()
        if record is None:
            raise NotFoundException(f"HACCP 점검 기록을 찾을 수 없습니다: {record_id}")
        if record.deleted_at is not None:
            raise ValidationException("이미 삭제된 HACCP 기록입니다")
        record.deleted_at = datetime.now(UTC)
        await self.db.flush()
        logger.warning(
            f"[HACCP] Record soft-deleted: id={record_id} deleted_by={deleted_by} "
            f"deleted_at={record.deleted_at.isoformat()}"
        )
