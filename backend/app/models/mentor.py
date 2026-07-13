"""
Модель ментора
Модель профиля ментора с информацией о специализации и опыте
"""

from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin


class Mentor(BaseModel, TimestampMixin):
    """Модель ментора"""

    __tablename__ = "mentors"
    __table_args__ = (
        Index("idx_mentor_available_rating", "is_available", "rating"),
        Index("idx_mentor_specialization", "specialization"),
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hourly_rate: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # в центах/копейках
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Связи
    user = relationship("User", back_populates="mentor_profile")
    sessions = relationship("Session", back_populates="mentor")
    courses = relationship("Course", back_populates="instructor")
    payments = relationship("Payment", back_populates="mentor")

    def __repr__(self):
        return f"<Mentor(id={self.id}, user_id={self.user_id}, specialization={self.specialization})>"
