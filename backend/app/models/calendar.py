"""
Модель интеграции календарей
Google Calendar + Outlook Calendar
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CalendarProvider(str, enum.Enum):
    """Провайдеры календарей"""

    GOOGLE = "google"
    OUTLOOK = "outlook"


class CalendarSync(BaseModel):
    """Модель синхронизации календаря пользователя"""

    __tablename__ = "calendar_syncs"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    provider = Column(SQLEnum(CalendarProvider), nullable=False)

    # OAuth токены
    access_token = Column(String(2048), nullable=False)
    refresh_token = Column(String(2048), nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=True)

    # ID календаря
    calendar_id = Column(String(255), nullable=True)  # Google calendar_id или Outlook calendar_id

    # Статус
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)

    # Настройки
    sync_past_days = Column(Integer, default=30, nullable=False)  # Синхронизировать события за N дней в прошлом
    sync_future_days = Column(Integer, default=90, nullable=False)  # Синхронизировать события за N дней в будущем
    auto_sync = Column(Boolean, default=True, nullable=False)  # Автоматическая синхронизация

    # Timestamp fields
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Связи
    user = relationship("User", backref="calendar_syncs")

    def __repr__(self):
        return f"<CalendarSync(user_id={self.user_id}, provider={self.provider.value})>"


class CalendarEvent(BaseModel):
    """Модель события календаря"""

    __tablename__ = "calendar_events"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(SQLEnum(CalendarProvider), nullable=False)
    external_id = Column(String(255), nullable=False, index=True)  # ID события в провайдере

    # Информация о событии
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(512), nullable=True)

    # Время
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_all_day = Column(Boolean, default=False, nullable=False)

    # Статус
    status = Column(String(50), nullable=True)  # confirmed, cancelled, tentative
    is_synced = Column(Boolean, default=True, nullable=False)  # Синхронизировано с MentorHub

    # Связь с сессиями MentorHub
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True, index=True)
    video_call_id = Column(Integer, ForeignKey("video_calls.id"), nullable=True, index=True)

    # Timestamp fields
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Связи
    user = relationship("User", backref="calendar_events")
    session = relationship("Session", backref="calendar_events")
    video_call = relationship("VideoCall", backref="calendar_events")

    __table_args__ = (
        # Уникальность по провайдеру и внешнему ID
        {'sqlite_autoincrement': True}  # Для SQLite совместимости
    )

    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title='{self.title}', start={self.start_time})>"
