"""
Firebase Cloud Messaging service
Сервис для отправки push-уведомлений через Firebase Cloud Messaging
"""

import logging
import json
from typing import List, Dict, Optional, Any
import httpx
from sqlalchemy.orm import Session

from app.models.device_token import DeviceToken
from app.config import settings

logger = logging.getLogger(__name__)


class FCMService:
    """Сервис для работы с Firebase Cloud Messaging"""
    
    def __init__(self):
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        self.server_key = settings.FCM_SERVER_KEY
        self.project_id = settings.FCM_PROJECT_ID
        
    async def send_notification(
        self,
        user_id: int,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Отправка push-уведомления пользователю
        
        Args:
            user_id: ID пользователя
            title: Заголовок уведомления
            body: Тело уведомления
            data: Дополнительные данные
            db: Сессия базы данных
            
        Returns:
            Результат отправки
        """
        if not db:
            logger.error("Database session required for sending notifications")
            return {"success": False, "error": "Database session required"}
            
        if not self.server_key:
            logger.warning("FCM_SERVER_KEY not configured")
            return {"success": False, "error": "FCM not configured"}
        
        # Получаем активные токены пользователя
        device_tokens = db.query(DeviceToken).filter(
            DeviceToken.user_id == user_id,
            DeviceToken.is_active == True
        ).all()
        
        if not device_tokens:
            logger.info(f"No active device tokens found for user {user_id}")
            return {"success": True, "message": "No devices registered"}
        
        # Формируем payload для каждого токена
        results = []
        for device_token in device_tokens:
            try:
                payload = self._build_payload(device_token.token, title, body, data)
                result = await self._send_to_fcm(payload)
                results.append({
                    "device_id": device_token.id,
                    "platform": device_token.platform,
                    "success": result.get("success", False),
                    "error": result.get("error")
                })
                
                # Если токен недействителен, деактивируем его
                if result.get("error") == "InvalidRegistration":
                    device_token.is_active = False
                    db.commit()
                    logger.warning(f"Deactivated invalid token {device_token.id}")
                    
            except Exception as e:
                logger.error(f"Error sending notification to device {device_token.id}: {e}")
                results.append({
                    "device_id": device_token.id,
                    "platform": device_token.platform,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        return {
            "success": success_count > 0,
            "total_devices": len(device_tokens),
            "successful_sends": success_count,
            "results": results
        }
    
    async def send_bulk_notification(
        self,
        user_ids: List[int],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Массовая отправка уведомлений группе пользователей
        """
        if not db:
            return {"success": False, "error": "Database session required"}
            
        results = []
        for user_id in user_ids:
            result = await self.send_notification(user_id, title, body, data, db)
            results.append({"user_id": user_id, **result})
        
        total_success = sum(1 for r in results if r["success"])
        return {
            "success": total_success > 0,
            "total_users": len(user_ids),
            "successful_users": total_success,
            "results": results
        }
    
    def _build_payload(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Формирование payload для FCM"""
        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default",
                "badge": "1"
            },
            "data": data or {},
            "android": {
                "priority": "high",
                "notification": {
                    "channel_id": "default_channel",
                    "sound": "default"
                }
            },
            "apns": {
                "headers": {
                    "apns-priority": "10"
                },
                "payload": {
                    "aps": {
                        "alert": {
                            "title": title,
                            "body": body
                        },
                        "sound": "default",
                        "badge": 1
                    }
                }
            }
        }
        return payload
    
    async def _send_to_fcm(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка payload в FCM"""
        headers = {
            "Authorization": f"key={self.server_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.fcm_url,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    success = result.get("success", 0) > 0
                    return {"success": success}
                else:
                    error_msg = f"FCM API error: {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text}"
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            logger.error(f"Error sending to FCM: {e}")
            return {"success": False, "error": str(e)}
    
    async def register_device_token(
        self,
        user_id: int,
        token: str,
        platform: str,
        device_name: Optional[str] = None,
        db: Session = None
    ) -> DeviceToken:
        """
        Регистрация токена устройства
        
        Args:
            user_id: ID пользователя
            token: Токен устройства
            platform: Платформа (ios/android/web)
            device_name: Название устройства
            db: Сессия базы данных
            
        Returns:
            Объект DeviceToken
        """
        if not db:
            raise ValueError("Database session required")
            
        # Проверяем, существует ли уже такой токен
        existing_token = db.query(DeviceToken).filter(
            DeviceToken.token == token
        ).first()
        
        if existing_token:
            # Если токен принадлежит другому пользователю, обновляем владельца
            if existing_token.user_id != user_id:
                existing_token.user_id = user_id
                existing_token.is_active = True
                existing_token.platform = platform
                existing_token.device_name = device_name
                db.commit()
            return existing_token
        
        # Создаем новый токен
        device_token = DeviceToken(
            user_id=user_id,
            token=token,
            platform=platform,
            device_name=device_name,
            is_active=True
        )
        db.add(device_token)
        db.commit()
        db.refresh(device_token)
        
        return device_token
    
    async def unregister_device_token(
        self,
        user_id: int,
        token: str,
        db: Session = None
    ) -> bool:
        """
        Удаление токена устройства
        
        Args:
            user_id: ID пользователя
            token: Токен устройства
            db: Сессия базы данных
            
        Returns:
            Успешность операции
        """
        if not db:
            return False
            
        device_token = db.query(DeviceToken).filter(
            DeviceToken.user_id == user_id,
            DeviceToken.token == token
        ).first()
        
        if device_token:
            db.delete(device_token)
            db.commit()
            return True
        return False

# Глобальный экземпляр сервиса
fcm_service = FCMService()