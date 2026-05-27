"""
Модели базы данных
Все модели SQLAlchemy должны быть импортированы здесь для обнаружения Alembic
"""

from app.models.achievement import Achievement
from app.models.base import BaseModel, TimestampMixin
from app.models.calendar import CalendarEvent, CalendarProvider, CalendarSync
from app.models.chat_room import ChatMessage, ChatRoom
from app.models.course import Course, CourseEnrollment, Lesson
from app.models.device_token import DeviceToken
from app.models.mentor import Mentor
from app.models.message import Message
from app.models.notification import Notification
from app.models.payment import Payment, PaymentStatus
from app.models.progress import Progress
from app.models.review import Review
from app.models.session import Session, SessionStatus
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionTier
from app.models.user import User, UserRole
from app.models.video_call import CallStatus, CallType, VideoCall

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
