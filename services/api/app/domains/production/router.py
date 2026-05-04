import uuid
import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.production.schemas import (
    ProcessCreate, ProcessRecordCreate, ProcessRecordResponse, ProcessRecordUpdate,
    ProcessResponse, ProductionLineCreate, ProductionLineResponse,
    WorkOrderCreate, WorkOrderListResponse, WorkOrderResponse, WorkOrderUpdate,
)
from app.domains.production.service import ProductionService
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/production", tags=["생산관리"])


def get_production_service(db: AsyncSession = Depends(get_db)) -> ProductionService:
    return ProductionService(db)


@router.get("/work-orders", response_model=WorkOrderListResponse)
async def list_work_orders(
    status: str | None = Query(None, description="PLANNED | IN_PROGRESS | COMPLETED | CANCELLED"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] GET /production/work-orders status={status} skip={skip} limit={limit}")
    return await service.list_work_orders(status=status, skip=skip, limit=limit)


@router.post("/work-orders", response_model=WorkOrderResponse, status_code=201)
async def create_work_order(
    payload: WorkOrderCreate,
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] POST /production/work-orders code={payload.code}")
    return await service.create_work_order(payload)


@router.get("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
async def get_work_order(
    work_order_id: uuid.UUID,
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] GET /production/work-orders/{work_order_id}")
    return await service.get_work_order(work_order_id)


@router.patch("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
async def update_work_order(
    work_order_id: uuid.UUID,
    payload: WorkOrderUpdate,
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] PATCH /production/work-orders/{work_order_id}")
    return await service.update_work_order(work_order_id, payload)


@router.post("/work-orders/{work_order_id}/start", response_model=WorkOrderResponse)
async def start_work_order(
    work_order_id: uuid.UUID,
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] POST /production/work-orders/{work_order_id}/start")
    return await service.start_work_order(work_order_id)


@router.post("/work-orders/{work_order_id}/complete", response_model=WorkOrderResponse)
async def complete_work_order(
    work_order_id: uuid.UUID,
    actual_qty: Annotated[float, Body(embed=True, gt=0)],
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] POST /production/work-orders/{work_order_id}/complete actual_qty={actual_qty}")
    return await service.complete_work_order(work_order_id, actual_qty)


# ── Production Lines ──────────────────────────────────────────────────────────

@router.get("/lines", response_model=list[ProductionLineResponse])
async def list_production_lines(
    service: ProductionService = Depends(get_production_service),
):
    logger.info("[API] GET /production/lines")
    return await service.list_production_lines()


@router.post("/lines", response_model=ProductionLineResponse, status_code=201)
async def create_production_line(
    payload: ProductionLineCreate,
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] POST /production/lines code={payload.code}")
    return await service.create_production_line(payload)


# ── Processes ─────────────────────────────────────────────────────────────────

@router.get("/processes", response_model=list[ProcessResponse])
async def list_processes(
    line_id: int | None = Query(None),
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] GET /production/processes line_id={line_id}")
    return await service.list_processes(line_id=line_id)


@router.post("/processes", response_model=ProcessResponse, status_code=201)
async def create_process(
    payload: ProcessCreate,
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] POST /production/processes code={payload.code}")
    return await service.create_process(payload)


# ── Process Records ───────────────────────────────────────────────────────────

@router.get("/work-orders/{work_order_id}/records", response_model=list[ProcessRecordResponse])
async def list_process_records(
    work_order_id: int,
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] GET /production/work-orders/{work_order_id}/records")
    return await service.list_process_records(work_order_id)


@router.post("/process-records", response_model=ProcessRecordResponse, status_code=201)
async def create_process_record(
    payload: ProcessRecordCreate,
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] POST /production/process-records work_order_id={payload.work_order_id}")
    return await service.create_process_record(payload)


@router.patch("/process-records/{record_id}", response_model=ProcessRecordResponse)
async def update_process_record(
    record_id: int,
    payload: ProcessRecordUpdate,
    service: ProductionService = Depends(get_production_service),
):
    logger.info(f"[API] PATCH /production/process-records/{record_id}")
    return await service.update_process_record(record_id, payload)
