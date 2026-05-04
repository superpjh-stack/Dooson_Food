import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.notification.schemas import NotificationResponse
from app.domains.notification.service import NotificationService
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["알림"])


def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get("", response_model=list[NotificationResponse])
async def list_unread(
    limit: int = Query(50, ge=1, le=200),
    service: NotificationService = Depends(get_notification_service),
):
    logger.info(f"[API] GET /notifications limit={limit}")
    return await service.list_unread(limit=limit)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: str,
    service: NotificationService = Depends(get_notification_service),
):
    logger.info(f"[API] POST /notifications/{notification_id}/read")
    return await service.mark_read(notification_id)


@router.post("/read-all")
async def mark_all_read(
    service: NotificationService = Depends(get_notification_service),
):
    logger.info("[API] POST /notifications/read-all")
    count = await service.mark_all_read()
    return {"message": f"{count}개의 알림을 읽음 처리했습니다", "count": count}
