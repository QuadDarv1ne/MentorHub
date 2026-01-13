"""
Push notifications API endpoints
API для управления push-уведомлениями через Firebase Cloud Messaging
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.device_token import DeviceToken
from app.utils.fcm import fcm_service
from app.config import settings
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/push-notifications", tags=["Push Notifications"])


class DeviceTokenRegisterRequest:
    """Схема для регистрации токена устройства"""
    token: str
    platform: str  # ios, android, web
    device_name: str = None


class PushNotificationRequest:
    """Схема для отправки push-уведомления"""
    title: str
    body: str
    data: dict = None
    user_ids: List[int] = None  # Если указано, отправляется группе пользователей


@router.post("/devices/register", response_model=SuccessResponse)
async def register_device_token(
    request: DeviceTokenRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Регистрация токена устройства для push-уведомлений
    
    Args:
        request: Данные токена устройства
        current_user: Текущий авторизованный пользователь
        db: Сессия базы данных
        
    Returns:
        Подтверждение регистрации
    """
    if not settings.PUSH_NOTIFICATIONS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Push notifications are disabled"
        )
    
    if not settings.FCM_SERVER_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="FCM not configured"
        )
    
    try:
        # Регистрируем токен
        device_token = await fcm_service.register_device_token(
            user_id=current_user.id,
            token=request.token,
            platform=request.platform.lower(),
            device_name=request.device_name,
            db=db
        )
        
        logger.info(f"Device token registered for user {current_user.id}")
        
        return SuccessResponse(
            success=True,
            message="Device token registered successfully"
        )
        
    except Exception as e:
        logger.error(f"Error registering device token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register device token"
        )


@router.delete("/devices/unregister", response_model=SuccessResponse)
async def unregister_device_token(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление токена устройства
    
    Args:
        token: Токен устройства для удаления
        current_user: Текущий авторизованный пользователь
        db: Сессия базы данных
        
    Returns:
        Подтверждение удаления
    """
    try:
        success = await fcm_service.unregister_device_token(
            user_id=current_user.id,
            token=token,
            db=db
        )
        
        if success:
            logger.info(f"Device token unregistered for user {current_user.id}")
            return SuccessResponse(
                success=True,
                message="Device token unregistered successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device token not found"
            )
            
    except Exception as e:
        logger.error(f"Error unregistering device token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unregister device token"
        )


@router.get("/devices", response_model=dict)
async def get_user_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка зарегистрированных устройств пользователя
    
    Args:
        current_user: Текущий авторизованный пользователь
        db: Сессия базы данных
        
    Returns:
        Список устройств
    """
    try:
        devices = db.query(DeviceToken).filter(
            DeviceToken.user_id == current_user.id
        ).all()
        
        return {
            "success": True,
            "devices": [
                {
                    "id": device.id,
                    "platform": device.platform,
                    "device_name": device.device_name,
                    "is_active": device.is_active,
                    "created_at": device.created_at.isoformat() if device.created_at else None
                }
                for device in devices
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching user devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch devices"
        )


@router.post("/send", response_model=dict)
async def send_push_notification(
    request: PushNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отправка push-уведомления
    
    Args:
        request: Данные уведомления
        current_user: Текущий авторизованный пользователь (должен быть админ)
        db: Сессия базы данных
        
    Returns:
        Результат отправки
    """
    # Проверяем права администратора
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can send push notifications"
        )
    
    if not settings.PUSH_NOTIFICATIONS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Push notifications are disabled"
        )
    
    try:
        if request.user_ids:
            # Массовая отправка группе пользователей
            result = await fcm_service.send_bulk_notification(
                user_ids=request.user_ids,
                title=request.title,
                body=request.body,
                data=request.data,
                db=db
            )
        else:
            # Отправка всем пользователям (можно добавить пагинацию)
            all_users = db.query(User).filter(User.is_active == True).all()
            user_ids = [user.id for user in all_users]
            
            result = await fcm_service.send_bulk_notification(
                user_ids=user_ids,
                title=request.title,
                body=request.body,
                data=request.data,
                db=db
            )
        
        logger.info(f"Push notification sent by admin {current_user.id}")
        
        return {
            "success": result["success"],
            "message": "Push notifications sent",
            "details": result
        }
        
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send push notification"
        )


@router.post("/send-to-user/{user_id}", response_model=dict)
async def send_push_to_user(
    user_id: int,
    request: PushNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отправка push-уведомления конкретному пользователю
    
    Args:
        user_id: ID получателя
        request: Данные уведомления
        current_user: Текущий авторизованный пользователь (должен быть админ)
        db: Сессия базы данных
        
    Returns:
        Результат отправки
    """
    # Проверяем права администратора
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can send push notifications"
        )
    
    # Проверяем существование пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        result = await fcm_service.send_notification(
            user_id=user_id,
            title=request.title,
            body=request.body,
            data=request.data,
            db=db
        )
        
        logger.info(f"Push notification sent to user {user_id} by admin {current_user.id}")
        
        return {
            "success": result["success"],
            "message": "Push notification sent",
            "details": result
        }
        
    except Exception as e:
        logger.error(f"Error sending push notification to user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send push notification"
        )


@router.get("/status", response_model=dict)
async def get_push_notification_status():
    """
    Получение статуса push-уведомлений
    
    Returns:
        Статус сервиса
    """
    return {
        "success": True,
        "enabled": settings.PUSH_NOTIFICATIONS_ENABLED,
        "fcm_configured": bool(settings.FCM_SERVER_KEY),
        "project_id": settings.FCM_PROJECT_ID if settings.FCM_PROJECT_ID else None
    }