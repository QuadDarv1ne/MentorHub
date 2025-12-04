"""
Модель трекинга прогресса пользователя по курсам/урокам
"""

from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin

class Progress(BaseModel, TimestampMixin):
    """Модель для хранения прогресса пользователя по курсам и урокам."""

    __tablename__ = "progress"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True, index=True)
    progress_percent = Column(Integer, default=0, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)

    # Связи
    user = relationship("User", back_populates="progress_records")
    course = relationship("Course", back_populates="progress_records")
    lesson = relationship("Lesson", back_populates="progress_records")

    def __repr__(self):
        return f"<Progress(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, progress={self.progress_percent})>"
