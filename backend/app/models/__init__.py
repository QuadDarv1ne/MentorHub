"""
Database Models
All SQLAlchemy models should be imported here for Alembic to discover them
"""

from app.models.base import BaseModel, TimestampMixin
from app.models.user import User, UserRole

# Import all models here for Alembic autogenerate
# Example:
# from app.models.mentor import Mentor
# from app.models.course import Course
# from app.models.session import Session

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "User",
    "UserRole",
]

