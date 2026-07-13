"""
Модель трекинга прогресса пользователя по курсам/урокам
"""

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin


class Progress(BaseModel, TimestampMixin):
    """Модель для хранения прогресса пользователя по курсам и урокам."""

    __tablename__ = "progress"
    __table_args__ = (
        Index("idx_progress_user_course", "user_id", "course_id"),
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    lesson_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("lessons.id"), nullable=True, index=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Связи
    user = relationship("User", back_populates="progress_records")
    course = relationship("Course", back_populates="progress_records")
    lesson = relationship("Lesson", back_populates="progress_records")

    def __repr__(self):
        return f"<Progress(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, progress={self.progress_percent})>"
