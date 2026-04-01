"""
Notifications Service
Бизнес-логика для управления уведомлениями
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func

from app.models.user import User
from app.models.notification import Notification, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для управления уведомлениями"""

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def get_notifications(
        self,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None
    ) -> List[Notification]:
        """Получить уведомления пользователя"""
        query = self.db.query(Notification).filter(
            Notification.user_id == self.user.id
        )

        if unread_only:
            query = query.filter(Notification.is_read == False)

        if notification_type:
            query = query.filter(Notification.type == notification_type)

        query = query.options(
            joinedload(Notification.user)
        ).order_by(
            desc(Notification.created_at)
        )

        return query.offset(skip).limit(limit).all()

    def get_unread_count(self) -> int:
        """Получить количество непрочитанных уведомлений"""
        return self.db.query(func.count(Notification.id)).filter(
            Notification.user_id == self.user.id,
            Notification.is_read == False
        ).scalar() or 0

    def mark_as_read(self, notification_id: int) -> bool:
        """Отметить уведомление как прочитанное"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == self.user.id
        ).first()

        if not notification:
            return False

        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def mark_all_as_read(self) -> int:
        """Отметить все уведомления как прочитанные"""
        result = self.db.query(Notification).filter(
            Notification.user_id == self.user.id,
            Notification.is_read == False
        ).update({
            Notification.is_read: True,
            Notification.read_at: datetime.now(timezone.utc)
        }, synchronize_session=False)

        self.db.commit()
        return result

    def delete_notification(self, notification_id: int) -> bool:
        """Удалить уведомление"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == self.user.id
        ).first()

        if not notification:
            return False

        self.db.delete(notification)
        self.db.commit()
        return True

    def delete_all_read(self) -> int:
        """Удалить все прочитанные уведомления"""
        result = self.db.query(Notification).filter(
            Notification.user_id == self.user.id,
            Notification.is_read == True
        ).delete(synchronize_session=False)

        self.db.commit()
        return result

    def create_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        link: Optional[str] = None
    ) -> Notification:
        """Создать уведомление"""
        notification = Notification(
            user_id=self.user.id,
            type=notification_type,
            title=title,
            message=message,
            data=json.dumps(data) if data else None,
            link=link,
            is_read=False
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        logger.info(f"Notification created for user {self.user.id}: {notification_type.value}")
        return notification

    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Удалить старые уведомления"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = self.db.query(Notification).filter(
            Notification.user_id == self.user.id,
            Notification.created_at < cutoff_date
        ).delete(synchronize_session=False)

        self.db.commit()
        logger.info(f"Cleaned up {result} old notifications for user {self.user.id}")
        return result


# Глобальные функции для создания уведомлений (без привязки к пользователю)
def create_notification(
    db: Session,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    link: Optional[str] = None
) -> Notification:
    """Создать уведомление для пользователя"""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        data=json.dumps(data) if data else None,
        link=link,
        is_read=False
    )

    self.db.add(notification)
    self.db.commit()
    self.db.refresh(notification)

    logger.info(f"Notification created for user {user_id}: {notification_type.value}")
    return notification


def send_bulk_notification(
    db: Session,
    user_ids: List[int],
    notification_type: NotificationType,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> int:
    """Отправить уведомление нескольким пользователям"""
    notifications = []
    for user_id in user_ids:
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=json.dumps(data) if data else None,
            is_read=False
        )
        notifications.append(notification)

    db.bulk_save_objects(notifications)
    db.commit()

    logger.info(f"Sent {len(notifications)} notifications to {len(user_ids)} users")
    return len(notifications)


def get_notification_service(db: Session, user: User) -> NotificationService:
    """Получить сервис уведомлений"""
    return NotificationService(db, user)
