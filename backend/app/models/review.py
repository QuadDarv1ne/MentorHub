"""
Модель отзыва о курсе
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin


class Review(BaseModel, TimestampMixin):
    """Модель отзывов пользователей о курсах."""

    __tablename__ = "reviews"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)  # stepik course id
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    # Отношение к пользователю
    user = relationship("User", backref="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, rating={self.rating})>"

    @property
    def user_name(self) -> str | None:
        """Возвращает читаемое имя пользователя (full_name или username)."""
        if hasattr(self, "user") and self.user is not None:
            return getattr(self.user, "full_name", None) or getattr(self.user, "username", None)
        return None
