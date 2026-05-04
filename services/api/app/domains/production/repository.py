import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.production.models import WorkOrder
from app.domains.production.schemas import WorkOrderCreate, WorkOrderUpdate


class ProductionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_work_order(self, data: WorkOrderCreate, code: str, bom_version: str | None) -> WorkOrder:
        wo = WorkOrder(
            code=code,
            product_id=data.product_id,
            production_line_id=data.production_line_id,
            planned_qty=data.planned_qty,
            unit=data.unit,
            planned_start=data.planned_start,
            planned_end=data.planned_end,
            bom_version=bom_version,
            notes=data.notes,
        )
        self.db.add(wo)
        await self.db.flush()
        return wo

    async def get_work_order(self, work_order_id: uuid.UUID) -> WorkOrder | None:
        result = await self.db.execute(select(WorkOrder).where(WorkOrder.id == work_order_id))
        return result.scalar_one_or_none()

    async def get_work_order_by_code(self, code: str) -> WorkOrder | None:
        result = await self.db.execute(select(WorkOrder).where(WorkOrder.code == code))
        return result.scalar_one_or_none()

    async def list_work_orders(
        self,
        status: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[WorkOrder], int]:
        stmt = select(WorkOrder)
        count_stmt = select(func.count()).select_from(WorkOrder)
        if status is not None:
            stmt = stmt.where(WorkOrder.status == status)
            count_stmt = count_stmt.where(WorkOrder.status == status)
        stmt = stmt.order_by(WorkOrder.planned_start.desc()).offset(skip).limit(limit)
        rows = await self.db.execute(stmt)
        count_row = await self.db.execute(count_stmt)
        return list(rows.scalars().all()), count_row.scalar_one()

    async def update_work_order(
        self, work_order_id: uuid.UUID, data: WorkOrderUpdate
    ) -> WorkOrder | None:
        wo = await self.get_work_order(work_order_id)
        if wo is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(wo, field, value)
        await self.db.flush()
        return wo
