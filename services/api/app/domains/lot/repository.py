import time
import uuid
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.lot.models import Lot, LotLineage
from app.shared.exceptions import LotNotFoundException


class LotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_filtered(
        self,
        status: str | None = None,
        lot_type: str | None = None,
        product_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Lot], int]:
        stmt = select(Lot)
        if status:
            stmt = stmt.where(Lot.status == status)
        if lot_type:
            stmt = stmt.where(Lot.type == lot_type)
        if product_id:
            stmt = stmt.where(Lot.product_id == product_id)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Lot.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, lot_id: uuid.UUID) -> Lot:
        result = await self.db.execute(select(Lot).where(Lot.id == lot_id))
        lot = result.scalar_one_or_none()
        if not lot:
            raise LotNotFoundException()
        return lot

    async def get_by_code(self, code: str) -> Lot:
        result = await self.db.execute(select(Lot).where(Lot.code == code))
        lot = result.scalar_one_or_none()
        if not lot:
            raise LotNotFoundException(f"LOT 코드 {code}를 찾을 수 없습니다")
        return lot

    async def create(self, lot: Lot) -> Lot:
        self.db.add(lot)
        await self.db.flush()
        # Always add self-referencing row (depth=0) for Closure Table
        self.db.add(LotLineage(ancestor_lot_id=lot.id, descendant_lot_id=lot.id, depth=0))
        return lot

    async def add_parent_links(
        self,
        child_id: uuid.UUID,
        parent_ids: list[uuid.UUID],
        qty_map: dict[str, Decimal],
    ) -> None:
        """Insert Closure Table rows: child→parent + child→all ancestors of parent."""
        for parent_id in parent_ids:
            qty = qty_map.get(str(parent_id))
            # Direct parent link (depth=1)
            self.db.add(
                LotLineage(
                    ancestor_lot_id=parent_id,
                    descendant_lot_id=child_id,
                    depth=1,
                    qty_used=qty,
                    relation_type="USED_IN",
                )
            )
            # Inherit all ancestor rows from parent (depth+1)
            stmt = select(LotLineage).where(
                LotLineage.descendant_lot_id == parent_id,
                LotLineage.depth > 0,
            )
            result = await self.db.execute(stmt)
            for ancestor_row in result.scalars().all():
                self.db.add(
                    LotLineage(
                        ancestor_lot_id=ancestor_row.ancestor_lot_id,
                        descendant_lot_id=child_id,
                        depth=ancestor_row.depth + 1,
                        relation_type="INDIRECT",
                    )
                )
        await self.db.flush()

    async def backward_trace(self, lot_id: uuid.UUID) -> tuple[list[dict], int]:
        """Fetch all ancestor LOTs (RAW/WIP) for a given LOT. Returns (nodes, ms)."""
        t0 = time.monotonic()
        stmt = (
            select(Lot, LotLineage.depth, LotLineage.qty_used, LotLineage.relation_type)
            .join(LotLineage, LotLineage.ancestor_lot_id == Lot.id)
            .where(LotLineage.descendant_lot_id == lot_id, LotLineage.depth > 0)
            .order_by(LotLineage.depth)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        ms = int((time.monotonic() - t0) * 1000)
        return [
            {"lot": row.Lot, "depth": row.depth, "qty_used": row.qty_used, "relation_type": row.relation_type}
            for row in rows
        ], ms

    async def forward_trace(self, lot_id: uuid.UUID) -> tuple[list[dict], int]:
        """Fetch all FG LOTs derived from a given (RAW/WIP) LOT."""
        t0 = time.monotonic()
        stmt = (
            select(Lot, LotLineage.depth, LotLineage.qty_used)
            .join(LotLineage, LotLineage.descendant_lot_id == Lot.id)
            .where(
                LotLineage.ancestor_lot_id == lot_id,
                LotLineage.depth > 0,
                Lot.type == "FG",
            )
            .order_by(LotLineage.depth)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        ms = int((time.monotonic() - t0) * 1000)
        return [
            {"lot": row.Lot, "depth": row.depth, "qty_used": row.qty_used, "relation_type": None}
            for row in rows
        ], ms

    async def recall_simulation(self, raw_lot_id: uuid.UUID) -> list[Lot]:
        """Find all FG lots that used this raw lot (for recall impact assessment)."""
        stmt = (
            select(Lot)
            .join(LotLineage, LotLineage.descendant_lot_id == Lot.id)
            .where(LotLineage.ancestor_lot_id == raw_lot_id, Lot.type == "FG")
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, lot: Lot, status: str) -> Lot:
        lot.status = status
        await self.db.flush()
        return lot
