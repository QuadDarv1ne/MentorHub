"""
Модель достижений
Модель для отслеживания достижений пользователей
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin


class Achievement(BaseModel, TimestampMixin):
    """Модель достижений пользователей"""

    __tablename__ = "achievements"

    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    earned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Связи
    user = relationship("User", backref="achievements")

    def __repr__(self):
        return f"<Achievement(id={self.id}, user_id={self.user_id}, title={self.title})>"
