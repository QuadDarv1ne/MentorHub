"""
Модель отзыва о курсе
"""

from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin


class Review(BaseModel, TimestampMixin):
    """Модель отзывов пользователей о курсах."""

    __tablename__ = "reviews"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)  # stepik course id
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    # Отношение к пользователю с cascade delete
    user = relationship("User", back_populates="reviews")

    # Уникальный constraint: один отзыв на курс от пользователя (защита от race condition)
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_review_user_course'),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, rating={self.rating})>"

    @property
    def user_name(self) -> str | None:
        """Возвращает читаемое имя пользователя (full_name или username)."""
        if hasattr(self, "user") and self.user is not None:
            return getattr(self.user, "full_name", None) or getattr(self.user, "username", None)
        return None
