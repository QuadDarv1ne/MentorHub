"""
Модель ментора
Модель профиля ментора с информацией о специализации и опыте
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel, TimestampMixin
from app.models.user import User


class Mentor(BaseModel, TimestampMixin):
    """Модель ментора"""

    __tablename__ = "mentors"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    bio = Column(Text, nullable=True)
    specialization = Column(String(255), nullable=True)
    experience_years = Column(Integer, default=0, nullable=False)
    hourly_rate = Column(Integer, default=0, nullable=False)  # в центах/копейках
    is_available = Column(Boolean, default=True, nullable=False)
    rating = Column(Float, default=0.0, nullable=False)
    total_sessions = Column(Integer, default=0, nullable=False)

    # Связи
    user = relationship("User", back_populates="mentor_profile")
    sessions = relationship("Session", back_populates="mentor")
    courses = relationship("Course", back_populates="instructor")

    def __repr__(self):
        return f"<Mentor(id={self.id}, user_id={self.user_id}, specialization={self.specialization})>"
