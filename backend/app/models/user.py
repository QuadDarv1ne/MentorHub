"""
Модель пользователя
Модель учетной записи и аутентификации пользователя
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel, TimestampMixin


class UserRole(str, enum.Enum):
    """Роли пользователей"""

    STUDENT = "student"
    MENTOR = "mentor"
    ADMIN = "admin"


class User(BaseModel, TimestampMixin):
    """Модель пользователя"""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)

    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Связи
    from sqlalchemy.orm import relationship
    mentor_profile = relationship("Mentor", back_populates="user", uselist=False)
    sessions_as_student = relationship("Session", foreign_keys="Session.student_id", back_populates="student")
    enrollments = relationship("CourseEnrollment", back_populates="user")
    progress_records = relationship("Progress", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
