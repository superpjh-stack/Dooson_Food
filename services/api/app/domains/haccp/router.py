import uuid
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.haccp.schemas import (
    HaccpCheckPlanCreate, HaccpCheckPlanResponse,
    HaccpCheckRecordCreate, HaccpCheckRecordResponse,
)
from app.domains.haccp.service import HaccpService
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/haccp", tags=["HACCP/식품안전"])


def get_haccp_service(db: AsyncSession = Depends(get_db)) -> HaccpService:
    return HaccpService(db)


@router.post("/check-plans", response_model=HaccpCheckPlanResponse, status_code=201)
async def create_check_plan(
    payload: HaccpCheckPlanCreate,
    service: HaccpService = Depends(get_haccp_service),
):
    logger.info(f"[API] POST /haccp/check-plans ccp={payload.ccp_id}")
    return await service.create_check_plan(payload)


@router.get("/check-plans", response_model=list[HaccpCheckPlanResponse])
async def list_check_plans(
    is_active: bool | None = Query(None),
    service: HaccpService = Depends(get_haccp_service),
):
    logger.info("[API] GET /haccp/check-plans")
    return await service.list_check_plans(is_active=is_active)


@router.post("/check-records", response_model=HaccpCheckRecordResponse, status_code=201)
async def create_check_record(
    payload: HaccpCheckRecordCreate,
    service: HaccpService = Depends(get_haccp_service),
):
    """HACCP 점검 기록 생성 — FAIL 시 LOT 자동 보류, 전자서명 감사로그 생성."""
    logger.info(f"[API] POST /haccp/check-records plan={payload.plan_id} result={payload.result}")
    return await service.create_check_record(payload)


@router.get("/check-records", response_model=list[HaccpCheckRecordResponse])
async def list_check_records(
    plan_id: uuid.UUID | None = Query(None),
    lot_id: uuid.UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: HaccpService = Depends(get_haccp_service),
):
    logger.info(f"[API] GET /haccp/check-records plan={plan_id} lot={lot_id}")
    return await service.list_check_records(plan_id=plan_id, lot_id=lot_id, skip=skip, limit=limit)


@router.get("/check-records/{record_id}", response_model=HaccpCheckRecordResponse)
async def get_check_record(
    record_id: uuid.UUID,
    service: HaccpService = Depends(get_haccp_service),
):
    logger.info(f"[API] GET /haccp/check-records/{record_id}")
    return await service.get_check_record(record_id)
