"""
Device Token model for Firebase Cloud Messaging
Модель токенов устройств для Firebase Cloud Messaging
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin


class DeviceToken(BaseModel, TimestampMixin):
    """Модель токена устройства для push-уведомлений"""
    
    __tablename__ = "device_tokens"
    
    # Связь с пользователем
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Токен устройства
    token = Column(String(512), nullable=False, unique=True, index=True)
    
    # Платформа устройства
    platform = Column(String(20), nullable=False)  # ios, android, web
    
    # Название устройства (опционально)
    device_name = Column(String(100), nullable=True)
    
    # Активен ли токен
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Связи
    user = relationship("User", back_populates="device_tokens")
    
    # Индексы
    __table_args__ = (
        Index('idx_device_tokens_user_active', 'user_id', 'is_active'),
        Index('idx_device_tokens_platform', 'platform'),
    )
    
    def __repr__(self):
        return f"<DeviceToken(id={self.id}, user_id={self.user_id}, platform={self.platform})>"