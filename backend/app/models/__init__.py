"""
Модели базы данных
Все модели SQLAlchemy должны быть импортированы здесь для обнаружения Alembic
"""

from app.models.base import BaseModel, TimestampMixin
from app.models.user import User, UserRole
from app.models.review import Review
from app.models.progress import Progress
from app.models.mentor import Mentor
from app.models.session import Session, SessionStatus
from app.models.message import Message
from app.models.payment import Payment, PaymentStatus
from app.models.achievement import Achievement
from app.models.course import Course, Lesson, CourseEnrollment
from app.models.device_token import DeviceToken
from app.models.notification import Notification
from app.models.chat_room import ChatRoom, ChatMessage
from app.models.video_call import VideoCall, CallType, CallStatus
from app.models.calendar import CalendarSync, CalendarEvent, CalendarProvider
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionTier

# Импортируйте все модели здесь для автогенерации Alembic

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "User",
    "UserRole",
    "Review",
    "Progress",
    "Mentor",
    "Session",
    "SessionStatus",
    "Message",
    "Payment",
    "PaymentStatus",
    "Achievement",
    "Course",
    "Lesson",
    "CourseEnrollment",
    "DeviceToken",
    "Notification",
    "ChatRoom",
    "ChatMessage",
    "VideoCall",
    "CallType",
    "CallStatus",
    "CalendarSync",
    "CalendarEvent",
    "CalendarProvider",
    "Subscription",
    "SubscriptionStatus",
    "SubscriptionTier",
]