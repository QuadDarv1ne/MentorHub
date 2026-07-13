"""
Notification system
Система уведомлений для пользователей
"""

import enum
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    __table_args__ = (
        Index("idx_notification_user_unread", "user_id", "is_read", "created_at"),
    )

    # Получатель
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Тип и содержание
    notification_type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType, name="notification_type_enum"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Дополнительные данные (JSON)
    data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string

    # Ссылка на связанный объект
    link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Статус
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Unix timestamp

    # Связи с cascade delete
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type.value}, user_id={self.user_id}, is_read={self.is_read})>"
