"""
Базовые модели
Общие базовые классы для всех моделей базы данных
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

from app.database import Base


class BaseModel(Base):
    """Базовая модель с общими полями"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    @declared_attr
    def __tablename__(cls):
        """Автоматическая генерация имени таблицы из имени класса"""
        return cls.__name__.lower() + "s"


class TimestampMixin:
    """Mixin для временных меток created_at и updated_at"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
