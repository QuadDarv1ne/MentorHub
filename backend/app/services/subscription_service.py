"""
Subscriptions Service
Бизнес-логика для управления подписками
"""

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session, joinedload

from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Сервис для управления подписками"""

    def __init__(self, db: Session):
        self.db = db

    # Тарифные планы
    PLANS: dict[str, dict[str, Any]] = {
        "basic": {
            "tier": "basic",
            "name": "Basic",
            "price": Decimal("9.99"),
            "currency": "USD",
            "trial_days": 14,
            "features": [
                "Доступ к базовым курсам",
                "2 сессии с ментором в месяц",
                "Доступ к сообществу",
            ]
        },
        "pro": {
            "tier": "pro",
            "name": "Pro",
            "price": Decimal("29.99"),
            "currency": "USD",
            "trial_days": 14,
            "features": [
                "Доступ ко всем курсам",
                "8 сессий с ментором в месяц",
                "Приоритетная поддержка",
                "Доступ к закрытым материалам",
            ]
        },
        "premium": {
            "tier": "premium",
            "name": "Premium",
            "price": Decimal("99.99"),
            "currency": "USD",
            "trial_days": 7,
            "features": [
                "Доступ ко всем курсам + новые материалы",
                "Безлимитные сессии с ментором",
                "Персональный ментор",
                "Помощь в трудоустройстве",
                "Доступ к VIP сообществу",
            ]
        },
    }

    def get_plans(self) -> list[dict[str, Any]]:
        """Получить список тарифных планов"""
        return list(self.PLANS.values())

    def get_plan(self, tier: str) -> dict[str, Any] | None:
        """Получить информацию о тарифе"""
        return self.PLANS.get(tier)

    def get_user_subscription(self, user_id: int) -> Subscription | None:
        """Получить активную подписку пользователя"""
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
        ).options(
            joinedload(Subscription.user)
        ).order_by(
            Subscription.created_at.desc()
        ).first()

    def create_subscription(
        self,
        user: User,
        tier: str,
        stripe_subscription_id: str | None = None
    ) -> Subscription:
        """Создать новую подписку"""
        try:
            plan = self.get_plan(tier)
            if not plan:
                raise ValueError(f"Invalid subscription tier: {tier}")

            # Проверяем существующую подписку
            existing = self.get_user_subscription(user.id)
            if existing and existing.status == SubscriptionStatus.ACTIVE:
                raise ValueError("User already has an active subscription")

            trial_end = datetime.now(timezone.utc) + timedelta(days=plan["trial_days"])

            subscription = Subscription(
                user_id=user.id,
                tier=tier,
                status=SubscriptionStatus.TRIAL,
                trial_end=trial_end,
                current_period_end=trial_end,
                amount=plan["price"],
                currency=plan["currency"],
                stripe_subscription_id=stripe_subscription_id,
                cancel_at_period_end=False
            )

            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            return subscription
        except ValueError:
            raise
        except Exception:
            logger.exception("Failed to create subscription for user %s", user.id)
            self.db.rollback()
            raise

    def activate_subscription(self, subscription_id: int) -> bool:
        """Активировать подписку"""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()

            if not subscription:
                return False

            subscription.status = SubscriptionStatus.ACTIVE
            self.db.commit()
            return True
        except Exception:
            logger.exception("Failed to activate subscription %s", subscription_id)
            self.db.rollback()
            raise

    def cancel_subscription(self, subscription_id: int, user_id: int) -> bool:
        """Отменить подписку (в конце периода)"""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id
            ).first()

            if not subscription:
                return False

            subscription.cancel_at_period_end = True
            self.db.commit()
            return True
        except Exception:
            logger.exception("Failed to cancel subscription %s for user %s", subscription_id, user_id)
            self.db.rollback()
            raise

    def reactivate_subscription(self, subscription_id: int, user_id: int) -> bool:
        """Восстановить подписку"""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id
            ).first()

            if not subscription:
                return False

            subscription.cancel_at_period_end = False
            self.db.commit()
            return True
        except Exception:
            logger.exception("Failed to reactivate subscription %s for user %s", subscription_id, user_id)
            self.db.rollback()
            raise

    def expire_subscription(self, subscription_id: int) -> bool:
        """Истечь подписку"""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()

            if not subscription:
                return False

            subscription.status = SubscriptionStatus.EXPIRED
            self.db.commit()
            return True
        except Exception:
            logger.exception("Failed to expire subscription %s", subscription_id)
            self.db.rollback()
            raise

    def upgrade_subscription(
        self,
        subscription_id: int,
        user_id: int,
        new_tier: str
    ) -> bool:
        """Обновить подписку на более высокий тариф"""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id
            ).first()

            if not subscription:
                return False

            plan = self.get_plan(new_tier)
            if not plan:
                return False

            subscription.tier = new_tier
            subscription.amount = plan["price"]
            self.db.commit()
            return True
        except Exception:
            logger.exception("Failed to upgrade subscription %s for user %s to tier %s", subscription_id, user_id, new_tier)
            self.db.rollback()
            raise

    def get_subscription_stats(self, user_id: int) -> dict[str, Any]:
        """Получить статистику подписки пользователя"""
        subscription = self.get_user_subscription(user_id)

        if not subscription:
            return {
                "has_subscription": False,
                "is_active": False,
                "is_trial": False,
            }

        now = datetime.now(timezone.utc)
        days_remaining = 0
        if subscription.current_period_end:
            days_remaining = (subscription.current_period_end - now).days

        return {
            "has_subscription": True,
            "is_active": subscription.status == SubscriptionStatus.ACTIVE,
            "is_trial": subscription.status == SubscriptionStatus.TRIAL,
            "tier": subscription.tier,
            "days_remaining": max(0, days_remaining),
            "cancel_at_period_end": subscription.cancel_at_period_end,
        }


# Глобальный экземпляр сервиса
def get_subscription_service(db: Session) -> SubscriptionService:
    """Получить сервис подписок"""
    return SubscriptionService(db)
