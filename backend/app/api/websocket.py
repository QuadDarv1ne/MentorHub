"""
WebSocket endpoints для real-time коммуникации
Чат между студентами и менторами + групповые чаты + уведомления
"""

import logging
import json
from typing import Dict, Set, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.user import User
from app.models.message import Message
from app.models.chat_room import ChatRoom, ChatMessage
from app.models.notification import Notification, NotificationType
from app.utils.security import decode_access_token

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Управление WebSocket соединениями"""

    def __init__(self):
        # user_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # room_id -> set of user_ids
        self.room_members: Dict[int, Set[int]] = {}
        # user_id -> set of room_ids
        self.user_rooms: Dict[int, Set[int]] = {}

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

    async def join_room(self, room_id: int, user_id: int):
        """Пользователь входит в чат-комнату"""
        if room_id not in self.room_members:
            self.room_members[room_id] = set()
        self.room_members[room_id].add(user_id)
        
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)
        
        logger.info(f"🏠 User {user_id} joined room {room_id}")

    async def leave_room(self, room_id: int, user_id: int):
        """Пользователь покидает чат-комнату"""
        if room_id in self.room_members:
            self.room_members[room_id].discard(user_id)
        if user_id in self.user_rooms:
            self.user_rooms[user_id].discard(room_id)
        
        logger.info(f"🚪 User {user_id} left room {room_id}")

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

    async def broadcast_to_room(self, room_id: int, message: dict, exclude_user_id: Optional[int] = None):
        """Отправка сообщения всем участникам комнаты"""
        if room_id not in self.room_members:
            return
            
        for user_id in self.room_members[room_id]:
            if user_id == exclude_user_id:
                continue
            await self.send_personal_message(message, user_id)

    async def broadcast_to_users(self, message: dict, user_ids: list):
        """Отправка сообщения нескольким пользователям"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)

    async def send_notification(self, user_id: int, notification: dict):
        """Отправка real-time уведомления"""
        await self.send_personal_message({
            "type": "notification",
            **notification
        }, user_id)

    def get_online_users(self) -> list:
        """Получить список онлайн пользователей"""
        return list(self.active_connections.keys())

    def is_user_online(self, user_id: int) -> bool:
        """Проверить, онлайн ли пользователь"""
        return user_id in self.active_connections

    def get_room_online_members(self, room_id: int) -> list:
        """Получить онлайн участников комнаты"""
        if room_id not in self.room_members:
            return []
        return [uid for uid in self.room_members[room_id] if uid in self.active_connections]


# Singleton instance
manager = ConnectionManager()


async def get_current_user_ws(
    token: str,
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
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint для чата

    Для аутентификации отправьте токен в первом сообщении:
    {
        "type": "auth",
        "token": "your_jwt_token"
    }

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
        # Получаем токен из первого сообщения
        data = await websocket.receive_json()

        if data.get("type") != "auth":
            await websocket.send_json({"type": "error", "message": "First message must be auth type"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        token = data.get("token")
        if not token:
            await websocket.send_json({"type": "error", "message": "Missing token"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

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
                
                # Real-time уведомление о новом сообщении
                if manager.is_user_online(recipient_id):
                    await manager.send_notification(recipient_id, {
                        "notification_type": NotificationType.NEW_MESSAGE.value,
                        "title": f"Новое сообщение от {user.username}",
                        "message": content[:100],
                        "link": f"/messages/{user.id}"
                    })

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
        except Exception as close_error:
            logger.debug(f"Failed to close websocket: {close_error}")


@router.websocket("/ws/room/{room_id}")
async def websocket_room_endpoint(
    room_id: int,
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint для комнатного чата

    Для аутентификации отправьте токен в первом сообщении:
    {
        "type": "auth",
        "token": "your_jwt_token"
    }

    Message format (client -> server):
    {
        "type": "message",
        "content": "Hello everyone!",
        "attachment_url": "https://...",
        "attachment_type": "image"
    }
    """
    user = None
    try:
        # Получаем токен из первого сообщения
        data = await websocket.receive_json()

        if data.get("type") != "auth":
            await websocket.send_json({"type": "error", "message": "First message must be auth type"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        token = data.get("token")
        if not token:
            await websocket.send_json({"type": "error", "message": "Missing token"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Аутентификация
        user = await get_current_user_ws(token=token, db=db)

        # Проверяем, что пользователь является участником комнаты
        room = db.query(ChatRoom).filter(
            ChatRoom.id == room_id,
            ChatRoom.members.any(User.id == user.id)
        ).first()

        if not room:
            await websocket.send_json({"type": "error", "message": "Room not found or you are not a member"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Подключение и вход в комнату
        await manager.connect(websocket, user.id)
        await manager.join_room(room_id, user.id)

        # Отправляем подтверждение
        await websocket.send_json({
            "type": "connected",
            "user_id": user.id,
            "username": user.username,
            "room_id": room_id,
            "room_name": room.name,
            "online_members": manager.get_room_online_members(room_id)
        })

        # Уведомляем других участников о входе
        await manager.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user.id,
            "username": user.username
        }, exclude_user_id=user.id)

        # Основной цикл
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "message":
                content = data.get("content", "").strip()
                attachment_url = data.get("attachment_url")
                attachment_type = data.get("attachment_type")
                parent_message_id = data.get("parent_message_id")

                if not content and not attachment_url:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Message must have content or attachment"
                    })
                    continue

                # Сохраняем сообщение
                chat_message = ChatMessage(
                    room_id=room_id,
                    sender_id=user.id,
                    content=content,
                    attachment_url=attachment_url,
                    attachment_type=attachment_type,
                    parent_message_id=parent_message_id
                )
                db.add(chat_message)
                
                # Обновляем updated_at у комнаты
                room.updated_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
                
                db.commit()
                db.refresh(chat_message)

                # Формируем ответ
                message_data = {
                    "type": "message",
                    "id": chat_message.id,
                    "room_id": room_id,
                    "sender_id": user.id,
                    "sender_username": user.username,
                    "sender_avatar": user.avatar_url,
                    "content": content,
                    "attachment_url": attachment_url,
                    "attachment_type": attachment_type,
                    "parent_message_id": parent_message_id,
                    "is_edited": False,
                    "is_deleted": False,
                    "timestamp": chat_message.created_at.isoformat()
                }

                # Отправляем отправителю и всем в комнате
                await websocket.send_json(message_data)
                await manager.broadcast_to_room(room_id, message_data, exclude_user_id=user.id)

                logger.info(f"📨 Room message {chat_message.id} in room {room_id} from {user.id}")

            elif message_type == "typing":
                await manager.broadcast_to_room(room_id, {
                    "type": "typing",
                    "user_id": user.id,
                    "username": user.username
                }, exclude_user_id=user.id)

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        if user:
            await manager.leave_room(room_id, user.id)
            manager.disconnect(websocket, user.id)
            
            # Уведомляем других участников о выходе
            await manager.broadcast_to_room(room_id, {
                "type": "user_left",
                "user_id": user.id,
                "username": user.username
            })
            
            logger.info(f"User {user.id} disconnected from room {room_id}")

    except Exception as e:
        logger.error(f"WebSocket room error: {e}")
        if user:
            await manager.leave_room(room_id, user.id)
            manager.disconnect(websocket, user.id)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception as close_error:
            logger.debug(f"Failed to close websocket: {close_error}")


@router.get("/ws/online-users")
async def get_online_users():
    """Получить список онлайн пользователей"""
    return {
        "online_users": manager.get_online_users(),
        "count": len(manager.get_online_users())
    }


@router.get("/ws/room/{room_id}/online")
async def get_room_online_members(room_id: int):
    """Получить онлайн участников комнаты"""
    return {
        "room_id": room_id,
        "online_members": manager.get_room_online_members(room_id),
        "count": len(manager.get_room_online_members(room_id))
    }
