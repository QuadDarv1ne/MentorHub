"""
Subscription model for recurring payments
Модель подписки для регулярных платежей
"""

import enum
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SubscriptionStatus(str, enum.Enum):
    """Статус подписки"""
    FREE = "free"  # Бесплатная подписка
    TRIAL = "trial"  # Пробный период
    ACTIVE = "active"  # Активна
    PAST_DUE = "past_due"  # Просрочена
    CANCELLED = "cancelled"  # Отменена
    EXPIRED = "expired"  # Истекла


class SubscriptionTier(str, enum.Enum):
    """Уровень подписки"""
    FREE = "free"  # Бесплатный
    BASIC = "basic"  # Базовый
    PRO = "pro"  # Продвинутый
    PREMIUM = "premium"  # Премиум


class Subscription(Base):
    """Модель подписки пользователя"""
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Stripe информация
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Информация о подписке
    tier: Mapped[SubscriptionTier] = mapped_column(Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE)
    status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.FREE)

    # Даты
    trial_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    trial_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Оплата
    amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)  # Сумма в месяц
    currency: Mapped[str] = mapped_column(String(10), default="USD")

    # Методы оплаты
    default_payment_method: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Stripe payment method ID

    # Флаги
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)  # Отменена в конце периода

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tier={self.tier}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Проверка активности подписки"""
        return self.status == SubscriptionStatus.ACTIVE

    @property
    def is_trial(self) -> bool:
        """Проверка пробного периода"""
        if self.trial_end and self.status == SubscriptionStatus.TRIAL:
            return bool(datetime.now(timezone.utc) < self.trial_end)
        return False

    @property
    def days_until_renewal(self) -> int:
        """Дней до следующего списания"""
        if self.current_period_end:
            delta = self.current_period_end - datetime.now(timezone.utc)
            return max(0, delta.days)
        return 0

    def to_dict(self) -> dict:
        """Конвертация в dict"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tier": self.tier.value,
            "status": self.status.value,
            "trial_start": self.trial_start.isoformat() if self.trial_start else None,
            "trial_end": self.trial_end.isoformat() if self.trial_end else None,
            "current_period_start": self.current_period_start.isoformat() if self.current_period_start else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "amount": float(self.amount) if self.amount else None,
            "currency": self.currency,
            "cancel_at_period_end": self.cancel_at_period_end,
            "days_until_renewal": self.days_until_renewal,
            "is_active": self.is_active,
            "is_trial": self.is_trial,
        }
