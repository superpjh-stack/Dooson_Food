import logging
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.notification.models import Notification
from app.domains.notification.schemas import NotificationCreate
from app.shared.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: NotificationCreate) -> Notification:
        notification = Notification(
            type=data.type,
            severity=data.severity,
            title=data.title,
            body=data.body,
            lot_id=data.lot_id,
            work_order_id=data.work_order_id,
        )
        self.db.add(notification)
        await self.db.flush()
        logger.info(
            f"[NOTIFICATION] Created type={data.type} severity={data.severity} title={data.title}"
        )

        # Broadcast via WebSocket (lazy import to avoid circular dependency with main.py)
        try:
            from app.main import broadcast_notification  # noqa: PLC0415
            await broadcast_notification({
                "id": str(notification.id),
                "type": notification.type,
                "severity": notification.severity,
                "title": notification.title,
                "body": notification.body,
            })
        except Exception as exc:
            logger.warning(f"[NOTIFICATION] WebSocket broadcast failed: {exc}")

        return notification

    async def list_unread(self, limit: int = 50) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.is_read.is_(False))
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def mark_read(self, notification_id: str) -> Notification:
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(stmt)
        notification = result.scalar_one_or_none()
        if notification is None:
            raise NotFoundException(f"알림을 찾을 수 없습니다: {notification_id}")
        notification.is_read = True
        notification.read_at = datetime.now(UTC)
        await self.db.flush()
        return notification

    async def mark_all_read(self) -> int:
        stmt = select(Notification).where(Notification.is_read.is_(False))
        result = await self.db.execute(stmt)
        notifications = result.scalars().all()
        now = datetime.now(UTC)
        count = 0
        for n in notifications:
            n.is_read = True
            n.read_at = now
            count += 1
        await self.db.flush()
        logger.info(f"[NOTIFICATION] Marked all read: {count} notifications")
        return count
