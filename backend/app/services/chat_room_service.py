"""
Chat Rooms Service
Бизнес-логика для управления чат-комнатами
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc

from app.models.user import User
from app.models.chat_room import ChatRoom, ChatMessage, chat_room_members
from app.schemas.chat_room import ChatRoomCreate, ChatRoomUpdate, ChatMessageCreate


class ChatRoomService:
    """Сервис для управления чат-комнатами"""

    def __init__(self, db: Session):
        self.db = db

    def create_chat_room(
        self,
        user: User,
        room_data: ChatRoomCreate
    ) -> ChatRoom:
        """Создать чат-комнату"""
        db_room = ChatRoom(
            name=room_data.name,
            description=room_data.description,
            created_by=user.id,
            is_private=room_data.is_private,
            course_id=room_data.course_id
        )
        self.db.add(db_room)
        self.db.commit()
        self.db.refresh(db_room)

        # Добавляем создателя как участника
        db_room.members.append(user)
        self.db.commit()
        self.db.refresh(db_room)

        return db_room

    def get_user_rooms(self, user_id: int, skip: int = 0, limit: int = 50) -> List[ChatRoom]:
        """Получить комнаты пользователя"""
        return self.db.query(ChatRoom).filter(
            ChatRoom.members.any(User.id == user_id)
        ).options(
            joinedload(ChatRoom.creator)
        ).order_by(
            desc(ChatRoom.updated_at)
        ).offset(skip).limit(limit).all()

    def get_room_by_id(self, room_id: int, user_id: int) -> Optional[ChatRoom]:
        """Получить комнату по ID с проверкой доступа"""
        return self.db.query(ChatRoom).filter(
            ChatRoom.id == room_id,
            ChatRoom.members.any(User.id == user_id)
        ).options(
            joinedload(ChatRoom.creator),
            joinedload(ChatRoom.members)
        ).first()

    def get_room_member_count(self, room_id: int) -> int:
        """Получить количество участников комнаты"""
        return self.db.query(func.count(chat_room_members.c.user_id)).filter(
            chat_room_members.c.chat_room_id == room_id
        ).scalar()

    def add_member(self, room_id: int, member_id: int) -> bool:
        """Добавить участника в комнату"""
        try:
            room = self.db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
            if not room:
                return False

            member = self.db.query(User).filter(User.id == member_id).first()
            if not member:
                return False

            if member not in room.members:
                room.members.append(member)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            raise

    def remove_member(self, room_id: int, member_id: int) -> bool:
        """Удалить участника из комнаты"""
        try:
            room = self.db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
            if not room:
                return False

            member = self.db.query(User).filter(User.id == member_id).first()
            if not member:
                return False

            if member in room.members:
                room.members.remove(member)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            raise

    def delete_room(self, room_id: int, user_id: int) -> bool:
        """Удалить комнату (только создатель)"""
        try:
            room = self.db.query(ChatRoom).filter(
                ChatRoom.id == room_id,
                ChatRoom.created_by == user_id
            ).first()

            if not room:
                return False

            self.db.delete(room)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def send_message(
        self,
        room_id: int,
        user: User,
        message_data: ChatMessageCreate
    ) -> ChatMessage:
        """Отправить сообщение в комнату"""
        try:
            # Проверяем, что пользователь является участником
            room = self.get_room_by_id(room_id, user.id)
            if not room:
                raise PermissionError("Вы не являетесь участником этой комнаты")

            db_message = ChatMessage(
                room_id=room_id,
                sender_id=user.id,
                content=message_data.content
            )
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            return db_message
        except PermissionError:
            raise
        except Exception:
            self.db.rollback()
            raise

    def get_room_messages(
        self,
        room_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Получить сообщения комнаты"""
        # Проверяем доступ
        room = self.get_room_by_id(room_id, user_id)
        if not room:
            raise PermissionError("Вы не являетесь участником этой комнаты")

        return self.db.query(ChatMessage).filter(
            ChatMessage.room_id == room_id
        ).options(
            joinedload(ChatMessage.sender)
        ).order_by(
            ChatMessage.sent_at
        ).offset(skip).limit(limit).all()


# Глобальная функция для форматирования ответа
def format_room_response(room: ChatRoom, member_count: int) -> Dict[str, Any]:
    """Форматирование ответа для комнаты"""
    return {
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "created_by": room.created_by,
        "is_private": room.is_private,
        "course_id": room.course_id,
        "created_at": room.created_at,
        "updated_at": room.updated_at,
        "member_count": member_count
    }
