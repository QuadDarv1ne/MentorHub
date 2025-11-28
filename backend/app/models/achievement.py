"""
Модель достижений
Модель для отслеживания достижений пользователей
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel, TimestampMixin


class Achievement(BaseModel, TimestampMixin):
    """Модель достижений пользователей"""

    __tablename__ = "achievements"

    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    user = relationship("User", backref="achievements")

    def __repr__(self):
        return f"<Achievement(id={self.id}, user_id={self.user_id}, title={self.title})>"