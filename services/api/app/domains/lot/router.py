import uuid
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.lot.schemas import (
    LotCreate, LotResponse, LotTraceResponse,
    LotForwardTraceResponse, RecallSimulationRequest, RecallSimulationResponse,
)
from app.domains.lot.service import LotService
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lots", tags=["LOT 트레이서빌리티"])


def get_lot_service(db: AsyncSession = Depends(get_db)) -> LotService:
    return LotService(db)


@router.get("")
async def list_lots(
    type: str | None = Query(None, description="RAW | WIP | FG"),
    status: str | None = Query(None),
    product_id: uuid.UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: LotService = Depends(get_lot_service),
):
    logger.info(f"[API] GET /lots type={type} status={status} skip={skip} limit={limit}")
    return await service.list(status=status, lot_type=type, skip=skip, limit=limit)


@router.post("", response_model=LotResponse, status_code=201)
async def create_lot(
    payload: LotCreate,
    service: LotService = Depends(get_lot_service),
):
    logger.info(f"[API] POST /lots code={payload.code}")
    lot = await service.create(payload)
    return lot


@router.get("/{lot_id}", response_model=LotResponse)
async def get_lot(
    lot_id: uuid.UUID,
    service: LotService = Depends(get_lot_service),
):
    logger.info(f"[API] GET /lots/{lot_id}")
    return await service.repo.get_by_id(lot_id)


@router.patch("/{lot_id}/hold", response_model=LotResponse)
async def hold_lot(
    lot_id: uuid.UUID,
    reason: str | None = None,
    held_by: str | None = None,
    service: LotService = Depends(get_lot_service),
):
    logger.info(f"[API] PATCH /lots/{lot_id}/hold reason={reason}")
    return await service.hold(lot_id, reason, held_by)


@router.patch("/{lot_id}/release", response_model=LotResponse)
async def release_lot(
    lot_id: uuid.UUID,
    service: LotService = Depends(get_lot_service),
):
    logger.info(f"[API] PATCH /lots/{lot_id}/release")
    return await service.release_hold(lot_id)


@router.get("/{lot_id}/trace/backward", response_model=LotTraceResponse)
async def backward_trace(
    lot_id: uuid.UUID,
    service: LotService = Depends(get_lot_service),
):
    """완제품 LOT → 사용된 원자재 LOT 역추적 (Closure Table O(1) 조회)"""
    logger.info(f"[API] GET /lots/{lot_id}/trace/backward")
    return await service.backward_trace(lot_id)


@router.get("/{lot_id}/trace/forward", response_model=LotForwardTraceResponse)
async def forward_trace(
    lot_id: uuid.UUID,
    service: LotService = Depends(get_lot_service),
):
    """원자재 LOT → 파생된 완제품 LOT 전방추적"""
    logger.info(f"[API] GET /lots/{lot_id}/trace/forward")
    return await service.forward_trace(lot_id)


@router.post("/recall-simulation", response_model=RecallSimulationResponse)
async def recall_simulation(
    payload: RecallSimulationRequest,
    service: LotService = Depends(get_lot_service),
):
    """회수 시뮬레이션: 문제 원자재 LOT가 영향을 미친 완제품 범위 파악"""
    logger.info(f"[API] POST /lots/recall-simulation raw_lot_id={payload.raw_lot_id}")
    return await service.recall_simulation(payload.raw_lot_id)
