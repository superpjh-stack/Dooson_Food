import logging
import uuid
from datetime import datetime, UTC

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.production.models import Process, ProcessRecord, ProductionLine, WorkOrder
from app.domains.production.repository import ProductionRepository
from app.domains.production.schemas import (
    ProcessCreate, ProcessRecordCreate, ProcessRecordResponse, ProcessRecordUpdate,
    ProcessResponse, ProductionLineCreate, ProductionLineResponse,
    WorkOrderCreate, WorkOrderListResponse, WorkOrderResponse, WorkOrderUpdate,
)
from app.shared.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class ProductionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductionRepository(db)

    async def _generate_code(self) -> str:
        """Auto-generate work order code: WO-{YYYYMMDD}-{seq:04d}."""
        today_str = datetime.now(UTC).strftime("%Y%m%d")
        prefix = f"WO-{today_str}-"
        count_stmt = select(func.count()).select_from(WorkOrder).where(WorkOrder.code.like(f"{prefix}%"))
        result = await self.db.execute(count_stmt)
        seq = (result.scalar_one() or 0) + 1
        return f"{prefix}{seq:04d}"

    async def create_work_order(self, data: WorkOrderCreate) -> WorkOrderResponse:
        code = data.code if data.code else await self._generate_code()
        # Lock BOM version at creation time — store as-is if provided, else record None
        bom_version = data.bom_version
        wo = await self.repo.create_work_order(data, code=code, bom_version=bom_version)
        logger.info(f"[PRODUCTION] WorkOrder created: {wo.code} bom_version={bom_version}")
        return WorkOrderResponse.model_validate(wo)

    async def get_work_order(self, work_order_id: uuid.UUID) -> WorkOrderResponse:
        wo = await self.repo.get_work_order(work_order_id)
        if wo is None:
            raise NotFoundException(f"생산지시를 찾을 수 없습니다: {work_order_id}")
        return WorkOrderResponse.model_validate(wo)

    async def list_work_orders(
        self, status: str | None = None, skip: int = 0, limit: int = 50
    ) -> WorkOrderListResponse:
        items, total = await self.repo.list_work_orders(status=status, skip=skip, limit=limit)
        return WorkOrderListResponse(
            items=[WorkOrderResponse.model_validate(w) for w in items],
            total=total,
        )

    async def update_work_order(
        self, work_order_id: uuid.UUID, data: WorkOrderUpdate
    ) -> WorkOrderResponse:
        wo = await self.repo.update_work_order(work_order_id, data)
        if wo is None:
            raise NotFoundException(f"생산지시를 찾을 수 없습니다: {work_order_id}")
        logger.info(f"[PRODUCTION] WorkOrder updated: {wo.code} status={wo.status}")
        return WorkOrderResponse.model_validate(wo)

    async def start_work_order(self, work_order_id: uuid.UUID) -> WorkOrderResponse:
        wo = await self.repo.get_work_order(work_order_id)
        if wo is None:
            raise NotFoundException(f"생산지시를 찾을 수 없습니다: {work_order_id}")
        if wo.status != "PLANNED":
            raise ValidationException(f"PLANNED 상태의 생산지시만 시작할 수 있습니다. 현재 상태: {wo.status}")
        wo.status = "IN_PROGRESS"
        wo.actual_start = datetime.now(UTC)
        await self.db.flush()
        logger.info(f"[PRODUCTION] WorkOrder started: {wo.code} actual_start={wo.actual_start}")
        return WorkOrderResponse.model_validate(wo)

    async def complete_work_order(
        self, work_order_id: uuid.UUID, actual_qty: float
    ) -> WorkOrderResponse:
        wo = await self.repo.get_work_order(work_order_id)
        if wo is None:
            raise NotFoundException(f"생산지시를 찾을 수 없습니다: {work_order_id}")
        if wo.status != "IN_PROGRESS":
            raise ValidationException(f"IN_PROGRESS 상태의 생산지시만 완료 처리할 수 있습니다. 현재 상태: {wo.status}")
        wo.status = "COMPLETED"
        wo.actual_end = datetime.now(UTC)
        wo.actual_qty = actual_qty
        await self.db.flush()
        logger.info(
            f"[PRODUCTION] WorkOrder completed: {wo.code} actual_qty={actual_qty} actual_end={wo.actual_end}"
        )
        return WorkOrderResponse.model_validate(wo)

    # ── ProductionLine ────────────────────────────────────────────────────────

    async def create_production_line(self, data: ProductionLineCreate) -> ProductionLineResponse:
        line = ProductionLine(**data.model_dump())
        self.db.add(line)
        await self.db.flush()
        logger.info(f"[PRODUCTION] ProductionLine created: {line.code} name={line.name}")
        return ProductionLineResponse.model_validate(line)

    async def list_production_lines(self) -> list[ProductionLineResponse]:
        result = await self.db.execute(
            select(ProductionLine).where(ProductionLine.is_active.is_(True)).order_by(ProductionLine.code)
        )
        return [ProductionLineResponse.model_validate(l) for l in result.scalars().all()]

    # ── Process ───────────────────────────────────────────────────────────────

    async def create_process(self, data: ProcessCreate) -> ProcessResponse:
        process = Process(**data.model_dump())
        self.db.add(process)
        await self.db.flush()
        logger.info(f"[PRODUCTION] Process created: {process.code} seq={process.sequence}")
        return ProcessResponse.model_validate(process)

    async def list_processes(self, line_id: int | None = None) -> list[ProcessResponse]:
        stmt = select(Process)
        if line_id is not None:
            stmt = stmt.where(Process.line_id == line_id)
        stmt = stmt.order_by(Process.sequence)
        result = await self.db.execute(stmt)
        return [ProcessResponse.model_validate(p) for p in result.scalars().all()]

    # ── ProcessRecord ─────────────────────────────────────────────────────────

    async def create_process_record(self, data: ProcessRecordCreate) -> ProcessRecordResponse:
        record = ProcessRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        logger.info(
            f"[PRODUCTION] ProcessRecord created: work_order_id={record.work_order_id} "
            f"process_id={record.process_id} status={record.status}"
        )
        return ProcessRecordResponse.model_validate(record)

    async def update_process_record(
        self, record_id: int, data: ProcessRecordUpdate
    ) -> ProcessRecordResponse:
        result = await self.db.execute(select(ProcessRecord).where(ProcessRecord.id == record_id))
        record = result.scalar_one_or_none()
        if record is None:
            raise NotFoundException(f"공정 실적을 찾을 수 없습니다: {record_id}")
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        await self.db.flush()
        logger.info(f"[PRODUCTION] ProcessRecord updated: id={record_id} status={record.status}")
        return ProcessRecordResponse.model_validate(record)

    async def list_process_records(self, work_order_id: int) -> list[ProcessRecordResponse]:
        result = await self.db.execute(
            select(ProcessRecord)
            .where(ProcessRecord.work_order_id == work_order_id)
            .order_by(ProcessRecord.id)
        )
        return [ProcessRecordResponse.model_validate(r) for r in result.scalars().all()]
