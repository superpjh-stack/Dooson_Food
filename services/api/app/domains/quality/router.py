import uuid
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.quality.schemas import (
    CcpRecordCreate, CcpRecordResponse, CcpResponse,
    FValueRecordCreate, FValueRecordResponse,
    FValueTemperatureCreate, FValueTemperatureResponse,
    XRayResultCreate, XRayResultResponse,
)
from app.domains.quality.service import QualityService
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quality", tags=["품질관리"])


def get_quality_service(db: AsyncSession = Depends(get_db)) -> QualityService:
    return QualityService(db)


@router.get("/ccps", response_model=list[CcpResponse])
async def list_ccps(service: QualityService = Depends(get_quality_service)):
    logger.info("[API] GET /quality/ccps")
    return await service.list_ccps()


@router.post("/ccp-records", response_model=CcpRecordResponse, status_code=201)
async def record_ccp(
    payload: CcpRecordCreate,
    service: QualityService = Depends(get_quality_service),
):
    """CCP 측정값 기록 — 이탈 시 자동으로 LOT 보류 + CRITICAL 알림 발송"""
    logger.info(f"[API] POST /quality/ccp-records ccp={payload.ccp_id} value={payload.measured_value}")
    return await service.record_ccp(payload)


@router.get("/ccp-records")
async def list_ccp_records(
    lot_id: uuid.UUID | None = Query(None),
    work_order_id: uuid.UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: QualityService = Depends(get_quality_service),
):
    logger.info(f"[API] GET /quality/ccp-records lot={lot_id} work_order={work_order_id}")
    return await service.list_ccp_records(lot_id=lot_id, work_order_id=work_order_id, skip=skip, limit=limit)


@router.patch("/ccp-records/{record_id}/corrective-action")
async def add_corrective_action(
    record_id: uuid.UUID,
    corrective_action: str,
    service: QualityService = Depends(get_quality_service),
):
    logger.info(f"[API] PATCH /quality/ccp-records/{record_id}/corrective-action")
    # TODO: implement
    return {"message": "시정조치가 기록되었습니다"}


@router.post("/f-value-records", response_model=FValueRecordResponse, status_code=201)
async def create_f_value_record(
    payload: FValueRecordCreate,
    service: QualityService = Depends(get_quality_service),
):
    logger.info(f"[API] POST /quality/f-value-records sterilizer={payload.sterilizer_id}")
    return await service.create_f_value_record(payload)


@router.get("/xray-results")
async def list_xray_results(
    result_filter: str | None = Query(None, alias="result"),
    lot_id: uuid.UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: QualityService = Depends(get_quality_service),
):
    logger.info(f"[API] GET /quality/xray-results result={result_filter} lot={lot_id}")
    return await service.list_xray_results(lot_id=lot_id, result_filter=result_filter, skip=skip, limit=limit)


@router.post("/xray-results", response_model=XRayResultResponse, status_code=201)
async def record_xray_result(
    payload: XRayResultCreate,
    service: QualityService = Depends(get_quality_service),
):
    """X-Ray 판정 결과 등록 — NG 판정 시 자동으로 LOT 보류 처리"""
    logger.info(f"[API] POST /quality/xray-results result={payload.result} lot={payload.lot_id}")
    return await service.record_xray_result(payload)


# ── F-value Temperature Series ────────────────────────────────────────────────

@router.post(
    "/f-value-records/{f_value_record_id}/temperatures",
    response_model=FValueTemperatureResponse,
    status_code=201,
)
async def append_f_value_temperature(
    f_value_record_id: int,
    payload: FValueTemperatureCreate,
    service: QualityService = Depends(get_quality_service),
):
    logger.info(
        f"[API] POST /quality/f-value-records/{f_value_record_id}/temperatures seq={payload.sequence}"
    )
    return await service.append_f_value_temperature(f_value_record_id, payload)


@router.get(
    "/f-value-records/{f_value_record_id}/temperatures",
    response_model=list[FValueTemperatureResponse],
)
async def list_f_value_temperatures(
    f_value_record_id: int,
    service: QualityService = Depends(get_quality_service),
):
    logger.info(f"[API] GET /quality/f-value-records/{f_value_record_id}/temperatures")
    return await service.list_f_value_temperatures(f_value_record_id)
