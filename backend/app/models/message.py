"""
Модель сообщения
Модель для обмена сообщениями между пользователями
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel


class Message(BaseModel):
    """Модель сообщения между пользователями"""
    
    __tablename__ = "messages"
    
    sender_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Timestamp fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
    # Связи
    # sender = relationship("User", foreign_keys=[sender_id])
    # recipient = relationship("User", foreign_keys=[recipient_id])
    
    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id})>"