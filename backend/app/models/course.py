"""
Модель курса
Модель для хранения информации о курсах
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin


class Course(BaseModel, TimestampMixin):
    """Модель курса"""

    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # beginner, intermediate, advanced
    duration_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # в центах/копейках
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    instructor_id: Mapped[int] = mapped_column(Integer, ForeignKey("mentors.id"), index=True, nullable=False)

    # Связи
    instructor = relationship("Mentor", back_populates="courses")
    enrollments = relationship("CourseEnrollment", back_populates="course")
    lessons = relationship("Lesson", back_populates="course")
    progress_records = relationship("Progress", back_populates="course")

    # Составные индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_course_category_active', 'category', 'is_active'),
        Index('idx_course_instructor_active', 'instructor_id', 'is_active'),
    )

    def __repr__(self):
        return f"<Course(id={self.id}, title={self.title}, instructor_id={self.instructor_id})>"


class Lesson(BaseModel, TimestampMixin):
    """Модель урока в курсе"""

    __tablename__ = "lessons"

    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_preview: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Связи
    course = relationship("Course", back_populates="lessons")
    progress_records = relationship("Progress", back_populates="lesson")

    # Составные индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_lesson_course_order', 'course_id', 'order'),
    )

    def __repr__(self):
        return f"<Lesson(id={self.id}, course_id={self.course_id}, title={self.title})>"


class CourseEnrollment(BaseModel, TimestampMixin):
    """Модель записи на курс"""

    __tablename__ = "course_enrollments"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), index=True, nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Связи с cascade delete
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    # Уникальный constraint: одна запись на курс от пользователя (защита от race condition)
    # Составные индексы для оптимизации запросов
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_enrollment_user_course'),
        Index('idx_enrollment_user_completed', 'user_id', 'completed'),
        Index('idx_enrollment_course_completed', 'course_id', 'completed'),
    )

    def __repr__(self):
        return f"<CourseEnrollment(id={self.id}, user_id={self.user_id}, course_id={self.course_id})>"
