"""
Модель видеозвонка
Интеграция с Agora для видеозвонков
"""

import enum
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class CallType(str, enum.Enum):
    """Типы звонков"""

    ONE_ON_ONE = "one_on_one"
    GROUP = "group"


class CallStatus(str, enum.Enum):
    """Статусы звонка"""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"


class VideoCall(BaseModel):
    """Модель видеозвонка"""

    __tablename__ = "video_calls"

    # Привязка к сессии менторинга
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sessions.id"), nullable=True, index=True)

    # Участники
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    call_type: Mapped[CallType] = mapped_column(SQLEnum(CallType), default=CallType.ONE_ON_ONE, nullable=False)

    # Для 1-on-1
    participant_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Для групповых звонков
    room_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("chat_rooms.id"), nullable=True, index=True)

    # Agora
    agora_channel: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    agora_token: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    # Статус
    status: Mapped[CallStatus] = mapped_column(SQLEnum(CallStatus), default=CallStatus.SCHEDULED, nullable=False, index=True)

    # Время
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Метаданные
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Timestamp fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Связи
    session = relationship("Session", foreign_keys=[session_id])
    creator = relationship("User", foreign_keys=[creator_id])
    participant = relationship("User", foreign_keys=[participant_id])
    chat_room = relationship("ChatRoom", backref="video_calls")

    @property
    def participants(self) -> list[Any]:
        """Возвращает список участников звонка (creator + participant)"""
        result = []
        if self.creator:
            result.append(self.creator)
        if self.participant and self.participant != self.creator:
            result.append(self.participant)
        return result

    def __repr__(self):
        return f"<VideoCall(id={self.id}, channel='{self.agora_channel}', status={self.status.value})>"
