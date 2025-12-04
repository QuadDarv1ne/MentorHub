"""
Модель курса
Модель для хранения информации о курсах
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel, TimestampMixin


class Course(BaseModel, TimestampMixin):
    """Модель курса"""

    __tablename__ = "courses"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    difficulty = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    duration_hours = Column(Integer, default=0, nullable=False)
    price = Column(Integer, default=0, nullable=False)  # в центах/копейках
    is_active = Column(Boolean, default=True, nullable=False)
    rating = Column(Float, default=0.0, nullable=False)
    total_reviews = Column(Integer, default=0, nullable=False)
    thumbnail_url = Column(String(512), nullable=True)
    instructor_id = Column(Integer, ForeignKey("mentors.id"), index=True, nullable=False)

    # Связи
    instructor = relationship("Mentor", back_populates="courses")
    enrollments = relationship("CourseEnrollment", back_populates="course")
    lessons = relationship("Lesson", back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.id}, title={self.title}, instructor_id={self.instructor_id})>"


class Lesson(BaseModel, TimestampMixin):
    """Модель урока в курсе"""

    __tablename__ = "lessons"

    course_id = Column(Integer, ForeignKey("courses.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    video_url = Column(String(512), nullable=True)
    duration_minutes = Column(Integer, default=0, nullable=False)
    order = Column(Integer, nullable=False)
    is_preview = Column(Boolean, default=False, nullable=False)

    # Связи
    course = relationship("Course", back_populates="lessons")
    # progress_records = relationship("Progress", back_populates="lesson")  # Временно отключено

    def __repr__(self):
        return f"<Lesson(id={self.id}, course_id={self.course_id}, title={self.title})>"


class CourseEnrollment(BaseModel, TimestampMixin):
    """Модель записи на курс"""

    __tablename__ = "course_enrollments"

    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), index=True, nullable=False)
    progress_percent = Column(Integer, default=0, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Связи
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<CourseEnrollment(id={self.id}, user_id={self.user_id}, course_id={self.course_id})>"