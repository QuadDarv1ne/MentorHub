"""
Модели базы данных
Все модели SQLAlchemy должны быть импортированы здесь для обнаружения Alembic
"""

from app.models.base import BaseModel, TimestampMixin
from app.models.user import User, UserRole

# Импортируйте все модели здесь для автогенерации Alembic
# Пример:
# from app.models.mentor import Mentor
# from app.models.course import Course
# from app.models.session import Session

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "User",
    "UserRole",
]

