"""
Модель интеграции календарей
Google Calendar + Outlook Calendar
"""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class CalendarProvider(str, enum.Enum):
    """Провайдеры календарей"""

    GOOGLE = "google"
    OUTLOOK = "outlook"


class CalendarSync(BaseModel):
    """Модель синхронизации календаря пользователя"""

    __tablename__ = "calendar_syncs"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    provider: Mapped[CalendarProvider] = mapped_column(SQLEnum(CalendarProvider), nullable=False)

    # OAuth токены
    access_token: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    token_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ID календаря
    calendar_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Google calendar_id или Outlook calendar_id

    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Настройки
    sync_past_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # Синхронизировать события за N дней в прошлом
    sync_future_days: Mapped[int] = mapped_column(Integer, default=90, nullable=False)  # Синхронизировать события за N дней в будущем
    auto_sync: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Автоматическая синхронизация

    # Timestamp fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
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

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider: Mapped[CalendarProvider] = mapped_column(SQLEnum(CalendarProvider), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # ID события в провайдере

    # Информация о событии
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Время
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Статус
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # confirmed, cancelled, tentative
    is_synced: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Синхронизировано с MentorHub

    # Связь с сессиями MentorHub
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=True, index=True)
    video_call_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("video_calls.id"), nullable=True, index=True)

    # Timestamp fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
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
