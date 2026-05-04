import uuid
import logging
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.lot.models import Lot
from app.domains.lot.repository import LotRepository
from app.domains.lot.schemas import (
    LotCreate, LotResponse, LotTraceResponse, LotForwardTraceResponse, RecallSimulationResponse,
)
from app.domains.notification.schemas import NotificationCreate
from app.domains.notification.service import NotificationService
from app.shared.exceptions import ValidationException

logger = logging.getLogger(__name__)


class LotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LotRepository(db)

    async def list(
        self,
        status: str | None = None,
        lot_type: str | None = None,
        product_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        items, total = await self.repo.list_filtered(
            status=status, lot_type=lot_type, product_id=product_id, skip=skip, limit=limit
        )
        return {
            "items": [LotResponse.model_validate(i) for i in items],
            "total": total,
            "page": skip // limit + 1,
            "limit": limit,
        }

    async def create(self, payload: LotCreate) -> Lot:
        logger.info(f"[LOT] CREATE code={payload.code} type={payload.type} qty={payload.qty}")

        lot = Lot(
            code=payload.code,
            type=payload.type,
            product_id=payload.product_id,
            work_order_id=payload.work_order_id,
            supplier_id=payload.supplier_id,
            qty=payload.qty,
            unit=payload.unit,
            received_at=payload.received_at,
            produced_at=payload.produced_at,
            expiry_date=payload.expiry_date,
            storage_location=payload.storage_location,
        )
        lot = await self.repo.create(lot)

        if payload.parent_lot_ids:
            await self.repo.add_parent_links(
                lot.id,
                payload.parent_lot_ids,
                payload.qty_used_per_parent,
            )
            logger.info(f"[LOT] LINEAGE linked {len(payload.parent_lot_ids)} parent(s) → {lot.code}")

        logger.info(f"[LOT] CREATED id={lot.id} code={lot.code}")
        return lot

    async def hold(self, lot_id: uuid.UUID, reason: str | None = None, held_by: str | None = None) -> Lot:
        lot = await self.repo.get_by_id(lot_id)
        if lot.status == "SHIPPED":
            raise ValidationException("출하된 LOT는 보류 처리할 수 없습니다")

        previous = lot.status
        lot = await self.repo.update_status(lot, "ON_HOLD")
        logger.warning(
            f"[LOT] HOLD id={lot.id} code={lot.code} {previous}→ON_HOLD "
            f"reason={reason} held_by={held_by}"
        )
        notification_service = NotificationService(self.db)
        await notification_service.create(NotificationCreate(
            type="LOT_HOLD",
            severity="CRITICAL",
            title=f"LOT {lot.code} 보류",
            body=f"사유: {reason or '미기재'}",
            lot_id=lot.id,
        ))
        return lot

    async def release_hold(self, lot_id: uuid.UUID) -> Lot:
        lot = await self.repo.get_by_id(lot_id)
        lot = await self.repo.update_status(lot, "ACTIVE")
        logger.info(f"[LOT] RELEASED id={lot.id} code={lot.code} ON_HOLD→ACTIVE")
        return lot

    async def backward_trace(self, lot_id: uuid.UUID) -> LotTraceResponse:
        target = await self.repo.get_by_id(lot_id)
        nodes, ms = await self.repo.backward_trace(lot_id)
        logger.info(f"[LOT] BACKWARD_TRACE lot={target.code} ancestors={len(nodes)} ms={ms}")
        return LotTraceResponse(target_lot=target, ancestors=nodes, query_ms=ms)

    async def forward_trace(self, lot_id: uuid.UUID) -> LotForwardTraceResponse:
        source = await self.repo.get_by_id(lot_id)
        nodes, ms = await self.repo.forward_trace(lot_id)
        logger.info(f"[LOT] FORWARD_TRACE lot={source.code} affected_fg={len(nodes)} ms={ms}")
        return LotForwardTraceResponse(source_lot=source, affected_fg_lots=nodes, query_ms=ms)

    async def recall_simulation(self, raw_lot_id: uuid.UUID) -> RecallSimulationResponse:
        source = await self.repo.get_by_id(raw_lot_id)
        if source.type != "RAW":
            raise ValidationException("회수 시뮬레이션은 원자재(RAW) LOT만 가능합니다")

        affected = await self.repo.recall_simulation(raw_lot_id)
        shipped = [lot for lot in affected if lot.status == "SHIPPED"]
        in_stock = [lot for lot in affected if lot.status in ("ACTIVE", "ON_HOLD")]

        logger.info(
            f"[LOT] RECALL_SIM source={source.code} affected={len(affected)} shipped={len(shipped)}"
        )
        return RecallSimulationResponse(
            source_lot=source,
            affected_lots=affected,
            total_affected=len(affected),
            shipped_count=len(shipped),
            in_stock_count=len(in_stock),
        )
