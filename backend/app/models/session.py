"""
Модель сессии
Модель для записи на сессии менторства
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SessionStatus(str, enum.Enum):
    """Статусы сессий"""

    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Session(BaseModel):
    """Модель сессии менторства"""

    __tablename__ = "sessions"

    student_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), index=True, nullable=False)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60, nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED, nullable=False)
    meeting_link = Column(String(512), nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamp fields
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Связи
    student = relationship("User", foreign_keys=[student_id], back_populates="sessions_as_student")
    mentor = relationship("Mentor", back_populates="sessions")
    payments = relationship("Payment", back_populates="session")

    # Составные индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_session_status_scheduled', 'status', 'scheduled_at'),
        Index('idx_session_student_status', 'student_id', 'status'),
        Index('idx_session_mentor_status', 'mentor_id', 'status'),
    )

    def __repr__(self):
        return f"<Session(id={self.id}, student_id={self.student_id}, mentor_id={self.mentor_id}, scheduled_at={self.scheduled_at})>"
