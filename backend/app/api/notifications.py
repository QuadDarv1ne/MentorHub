"""
Notification API endpoints
CRUD операции для уведомлений
"""

import logging
import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification, NotificationType
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class NotificationCreate(BaseModel):
    """Создание уведомления"""
    user_id: int
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None
    link: Optional[str] = None


class NotificationResponse(BaseModel):
    """Ответ с уведомлением"""
    id: int
    type: str
    title: str
    message: str
    data: Optional[dict] = None
    link: Optional[str] = None
    is_read: bool
    read_at: Optional[int] = None
    created_at: int
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Список уведомлений"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int


@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    type: Optional[NotificationType] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить уведомления текущего пользователя
    
    Query params:
    - skip: Сколько пропустить
    - limit: Максимум уведомлений
    - unread_only: Только непрочитанные
    - type: Фильтр по типу
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    # Фильтры
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    if type:
        query = query.filter(Notification.type == type)
    
    # Подсчет непрочитанных
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    # Сортировка и пагинация
    total = query.count()
    notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
    
    # Преобразование
    notification_responses = []
    for notif in notifications:
        data = json.loads(notif.data) if notif.data else None
        notification_responses.append(NotificationResponse(
            id=notif.id,
            type=notif.type.value,
            title=notif.title,
            message=notif.message,
            data=data,
            link=notif.link,
            is_read=notif.is_read,
            read_at=notif.read_at,
            created_at=notif.created_at
        ))
    
    return NotificationListResponse(
        notifications=notification_responses,
        total=total,
        unread_count=unread_count
    )


@router.get("/notifications/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить количество непрочитанных уведомлений"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": count}


@router.post("/notifications/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отметить уведомление как прочитанное"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = int(datetime.now(timezone.utc).timestamp())
        db.commit()
        db.refresh(notification)
    
    return {"message": "Уведомление отмечено как прочитанное"}


@router.post("/notifications/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отметить все уведомления как прочитанные"""
    updated = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({
        "is_read": True,
        "read_at": int(datetime.now(timezone.utc).timestamp())
    })
    
    db.commit()
    
    return {
        "message": "Все уведомления отмечены как прочитанные",
        "updated_count": updated
    }


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить уведомление"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    db.delete(notification)
    db.commit()
    
    return None


@router.delete("/notifications/clear-all", status_code=status.HTTP_200_OK)
async def clear_all_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить все прочитанные уведомления"""
    deleted = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == True
    ).delete()
    
    db.commit()
    
    return {
        "message": "Прочитанные уведомления удалены",
        "deleted_count": deleted
    }


# Helper функция для создания уведомлений
async def create_notification(
    db: Session,
    user_id: int,
    type: NotificationType,
    title: str,
    message: str,
    data: Optional[dict] = None,
    link: Optional[str] = None
) -> Notification:
    """
    Создать уведомление для пользователя
    
    Args:
        db: Database session
        user_id: ID пользователя
        type: Тип уведомления
        title: Заголовок
        message: Текст уведомления
        data: Дополнительные данные (dict)
        link: Ссылка на связанный объект
    
    Returns:
        Созданное уведомление
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        data=json.dumps(data) if data else None,
        link=link,
        is_read=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    logger.info(f"📬 Notification created: {type.value} for user {user_id}")
    
    return notification
