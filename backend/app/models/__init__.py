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
]

