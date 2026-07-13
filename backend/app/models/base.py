"""
Базовые модели
Общие базовые классы для всех моделей базы данных
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.database import Base


class BaseModel(Base):
    """Базовая модель с общими полями"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    @declared_attr
    def __tablename__(cls):
        """Автоматическая генерация имени таблицы из имени класса"""
        return cls.__name__.lower() + "s"


class TimestampMixin:
    """Mixin для временных меток created_at и updated_at"""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
