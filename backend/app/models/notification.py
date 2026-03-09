"""
Notification system
Система уведомлений для пользователей
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel, TimestampMixin


class NotificationType(str, enum.Enum):
    """Типы уведомлений"""
    
    # Сессии
    SESSION_SCHEDULED = "session_scheduled"
    SESSION_REMINDER = "session_reminder"
    SESSION_CANCELLED = "session_cancelled"
    SESSION_COMPLETED = "session_completed"
    
    # Сообщения
    NEW_MESSAGE = "new_message"
    
    # Курсы
    COURSE_ENROLLED = "course_enrolled"
    LESSON_COMPLETED = "lesson_completed"
    COURSE_UPDATED = "course_updated"
    
    # Платежи
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    
    # Достижения
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    
    # Отзывы
    NEW_REVIEW = "new_review"
    REVIEW_REPLY = "review_reply"
    
    # Система
    ACCOUNT_VERIFIED = "account_verified"
    PASSWORD_CHANGED = "password_changed"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class Notification(BaseModel, TimestampMixin):
    """Модель уведомления"""
    
    __tablename__ = "notifications"
    
    # Получатель
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Тип и содержание
    type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Дополнительные данные (JSON)
    data = Column(Text, nullable=True)  # JSON string
    
    # Ссылка на связанный объект
    link = Column(String(512), nullable=True)
    
    # Статус
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(Integer, nullable=True)  # Unix timestamp
    
    # Связи
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type.value}, user_id={self.user_id}, is_read={self.is_read})>"
