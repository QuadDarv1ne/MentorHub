"""
Модель пользователя
Модель учетной записи и аутентификации пользователя
"""

import enum

from sqlalchemy import Boolean, Column, Index, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

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
    hashed_password = Column(String(255), nullable=True)  # Может быть None для OAuth пользователей

    # OAuth поля
    oauth_provider = Column(String(50), nullable=True)  # "google", "github"
    oauth_id = Column(String(255), nullable=True)  # ID от OAuth провайдера

    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)

    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)  # OAuth пользователи верифицированы

    # 2FA поля
    two_factor_enabled = Column(Boolean, default=False, nullable=True)
    two_factor_secret = Column(String(255), nullable=True)  # Зашифрованный TOTP секрет

    # Связи
    mentor_profile = relationship("Mentor", back_populates="user", uselist=False)
    sessions_as_student = relationship("Session", foreign_keys="Session.student_id", back_populates="student")
    enrollments = relationship("CourseEnrollment", back_populates="user")
    progress_records = relationship("Progress", back_populates="user")
    reviews_given = relationship("Review", foreign_keys="Review.user_id", back_populates="reviewer")
    reviews_received = relationship("Review", foreign_keys="Review.reviewed_id", back_populates="reviewed")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    device_tokens = relationship("DeviceToken", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", foreign_keys="Payment.student_id", back_populates="student")
    chat_rooms = relationship("ChatRoom", secondary="chat_room_members", back_populates="members")
    chat_messages = relationship("ChatMessage", back_populates="sender", foreign_keys="ChatMessage.sender_id")
    subscription = relationship("Subscription", back_populates="user", uselist=False)

    # Составные индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_user_role_active', 'role', 'is_active'),
        Index('idx_user_email_active', 'email', 'is_active'),
    )

    @property
    def is_admin(self) -> bool:
        """Проверка является ли пользователь админом"""
        return self.role == UserRole.ADMIN

    @property
    def is_mentor(self) -> bool:
        """Проверка является ли пользователь ментором"""
        return self.role == UserRole.MENTOR

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
