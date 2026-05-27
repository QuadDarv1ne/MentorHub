"""
Модель отзыва о курсе
"""

from sqlalchemy import Column, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin


class Review(BaseModel, TimestampMixin):
    """Модель отзывов пользователей о курсах."""

    __tablename__ = "reviews"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reviewed_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # ID ментора, о котором отзыв
    course_id = Column(Integer, nullable=True, index=True)  # stepik course id (nullable for mentor reviews)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    # Отношение к пользователю с cascade delete
    # Review может быть связано как reviewer (оставивший отзыв) или reviewed (получивший отзыв)
    reviewer = relationship("User", foreign_keys=[user_id], back_populates="reviews_given")
    reviewed = relationship("User", foreign_keys="Review.reviewed_id", back_populates="reviews_received")

    # Уникальный constraint: один отзыв на курс от пользователя (защита от race condition)
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_review_user_course'),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, rating={self.rating})>"

    @property
    def user_name(self) -> str | None:
        """Возвращает читаемое имя пользователя (full_name или username)."""
        if hasattr(self, "reviewer") and self.reviewer is not None:
            return getattr(self.reviewer, "full_name", None) or getattr(self.reviewer, "username", None)
        return None
