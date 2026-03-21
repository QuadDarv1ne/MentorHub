"""
Модель чат-комнаты
Групповые чаты для курсов и проектов
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.models.base import BaseModel


# Association table для участников чат-комнаты
chat_room_members = Table(
    "chat_room_members",
    BaseModel.metadata,
    Column("chat_room_id", Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class ChatRoom(BaseModel):
    """Модель чат-комнаты"""

    __tablename__ = "chat_rooms"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_private = Column(Boolean, default=False, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)  # Для курсовых чатов
    
    # Timestamp fields
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Связи
    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("User", secondary=chat_room_members, back_populates="chat_rooms")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatRoom(id={self.id}, name='{self.name}', created_by={self.created_by})>"


class ChatMessage(BaseModel):
    """Модель сообщения в чат-комнате"""

    __tablename__ = "chat_messages"

    room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Вложения
    attachment_url = Column(String(512), nullable=True)
    attachment_type = Column(String(50), nullable=True)  # image, document, video
    
    # Для тредов
    parent_message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=True, index=True)
    
    # Timestamp fields
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Связи
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    parent = relationship("ChatMessage", remote_side="ChatMessage.id", backref="replies")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, room_id={self.room_id}, sender_id={self.sender_id})>"
