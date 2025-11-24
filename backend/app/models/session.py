"""
Модель сессии
Модель для записи на сессии менторства
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Связи
    # student = relationship("User", foreign_keys=[student_id], back_populates="sessions_as_student")
    # mentor = relationship("Mentor", back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, student_id={self.student_id}, mentor_id={self.mentor_id}, scheduled_at={self.scheduled_at})>"
