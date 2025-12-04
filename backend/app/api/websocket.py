"""
WebSocket endpoints для real-time коммуникации
Чат между студентами и менторами
"""

import logging
import json
from datetime import datetime
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.user import User
from app.models.message import Message
from app.utils.security import decode_access_token

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Управление WebSocket соединениями"""

    def __init__(self):
        # user_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Подключение нового клиента"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"✅ User {user_id} connected via WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Отключение клиента"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"❌ User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: dict, user_id: int):
        """Отправка сообщения конкретному пользователю"""
        if user_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(websocket)
            
            # Удаляем отключенные сокеты
            for ws in disconnected:
                self.active_connections[user_id].discard(ws)

    async def broadcast_to_users(self, message: dict, user_ids: list):
        """Отправка сообщения нескольким пользователям"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)

    def get_online_users(self) -> list:
        """Получить список онлайн пользователей"""
        return list(self.active_connections.keys())


# Singleton instance
manager = ConnectionManager()


async def get_current_user_ws(
    token: str = Query(...),
    db: Session = Depends(get_db)
) -> User:
    """Получить текущего пользователя из WebSocket токена"""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise ValueError("User not found")
        
        return user
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        raise


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint для чата
    
    Query params:
        - token: JWT access token для аутентификации
    
    Message format (client -> server):
    {
        "type": "message",
        "recipient_id": 123,
        "content": "Hello!"
    }
    
    Message format (server -> client):
    {
        "type": "message",
        "id": 456,
        "sender_id": 789,
        "sender_username": "john_doe",
        "content": "Hello!",
        "timestamp": "2025-12-04T12:00:00"
    }
    """
    user = None
    try:
        # Аутентификация
        user = await get_current_user_ws(token=token, db=db)
        
        # Подключение
        await manager.connect(websocket, user.id)
        
        # Отправляем подтверждение подключения
        await websocket.send_json({
            "type": "connected",
            "user_id": user.id,
            "username": user.username,
            "online_users": manager.get_online_users()
        })
        
        # Основной цикл приема сообщений
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "message":
                # Обработка текстового сообщения
                recipient_id = data.get("recipient_id")
                content = data.get("content", "").strip()
                
                if not recipient_id or not content:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Missing recipient_id or content"
                    })
                    continue
                
                # Сохраняем сообщение в БД
                message = Message(
                    sender_id=user.id,
                    recipient_id=recipient_id,
                    content=content,
                    is_read=False
                )
                db.add(message)
                db.commit()
                db.refresh(message)
                
                # Формируем ответ
                message_data = {
                    "type": "message",
                    "id": message.id,
                    "sender_id": user.id,
                    "sender_username": user.username,
                    "sender_avatar": user.avatar_url,
                    "recipient_id": recipient_id,
                    "content": content,
                    "timestamp": message.created_at.isoformat()
                }
                
                # Отправляем отправителю (подтверждение)
                await websocket.send_json(message_data)
                
                # Отправляем получателю
                await manager.send_personal_message(message_data, recipient_id)
                
                logger.info(f"📨 Message {message.id} from {user.id} to {recipient_id}")
            
            elif message_type == "typing":
                # Индикатор печати
                recipient_id = data.get("recipient_id")
                if recipient_id:
                    await manager.send_personal_message({
                        "type": "typing",
                        "user_id": user.id,
                        "username": user.username
                    }, recipient_id)
            
            elif message_type == "read":
                # Отметка о прочтении
                message_id = data.get("message_id")
                if message_id:
                    message = db.query(Message).filter(
                        Message.id == message_id,
                        Message.recipient_id == user.id
                    ).first()
                    
                    if message:
                        message.is_read = True
                        db.commit()
                        
                        # Уведомляем отправителя
                        await manager.send_personal_message({
                            "type": "read",
                            "message_id": message_id,
                            "reader_id": user.id
                        }, message.sender_id)
            
            elif message_type == "ping":
                # Keep-alive ping
                await websocket.send_json({"type": "pong"})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        if user:
            manager.disconnect(websocket, user.id)
            logger.info(f"User {user.id} disconnected normally")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user:
            manager.disconnect(websocket, user.id)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass


@router.get("/ws/online-users")
async def get_online_users():
    """Получить список онлайн пользователей"""
    return {
        "online_users": manager.get_online_users(),
        "count": len(manager.get_online_users())
    }
