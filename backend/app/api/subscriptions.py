"""
Роуты подписок
API для управления подписками пользователей
"""

from decimal import Decimal
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionTier
from app.services.subscription_service import get_subscription_service, SubscriptionService
from app.services.cache import cached
from app.services.stripe_service import stripe_service
from app.config import settings
from pydantic import BaseModel, Field

router = APIRouter()

# Тарифы подписок
SUBSCRIPTION_PLANS: Dict[str, Dict[str, Any]] = {
    "basic": {
        "tier": "basic",
        "name": "Basic",
        "price": Decimal("9.99"),
        "currency": "USD",
        "trial_days": 14,
        "features": ["Доступ к базовым курсам", "Чат с менторами", "1 сессия в месяц"],
    },
    "pro": {
        "tier": "pro",
        "name": "Pro",
        "price": Decimal("29.99"),
        "currency": "USD",
        "trial_days": 14,
        "features": ["Доступ ко всем курсам", "Приоритетная поддержка", "5 сессий в месяц", "Записи видео"],
    },
    "premium": {
        "tier": "premium",
        "name": "Premium",
        "price": Decimal("59.99"),
        "currency": "USD",
        "trial_days": 14,
        "features": ["Всё из Pro", "Безлимитные сессии", "Персональный ментор", "Приоритетная поддержка 24/7"],
    },
}


class SubscriptionPlan(BaseModel):
    """Информация о тарифе"""
    tier: str
    name: str
    price: Decimal
    currency: str
    trial_days: int = 14
    features: list = Field(default_factory=list)


class CreateSubscriptionRequest(BaseModel):
    """Запрос на создание подписки"""
    tier: str = Field(..., description="Уровень подписки: basic, pro, premium")


class SubscriptionResponse(BaseModel):
    """Ответ с информацией о подписке"""
    id: int
    tier: str
    status: str
    trial_end: Optional[str] = None
    current_period_end: Optional[str] = None
    amount: Optional[float] = None
    currency: str
    cancel_at_period_end: bool
    days_until_renewal: int
    is_active: bool
    is_trial: bool


def _get_service(db: Session = Depends(get_db)) -> SubscriptionService:
    """Получить сервис подписок"""
    return get_subscription_service(db)


@router.get("/plans", response_model=list[SubscriptionPlan])
@cached(ttl=3600, key_prefix="subscription_plans")
async def get_subscription_plans(
    service: SubscriptionService = Depends(_get_service)
):
    """Получить список тарифных планов"""
    plans = service.get_plans()
    return [SubscriptionPlan(**plan) for plan in plans]


@router.get("/my", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    service: SubscriptionService = Depends(_get_service)
):
    """Получить информацию о подписке текущего пользователя"""
    subscription = service.get_user_subscription(current_user.id)

    if not subscription:
        # Создаём бесплатную подписку по умолчанию
        from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionTier
        subscription = Subscription(
            user_id=current_user.id,
            tier=SubscriptionTier.FREE,
            status=SubscriptionStatus.FREE,
            currency="USD",
        )
        service.db.add(subscription)
        service.db.commit()
        service.db.refresh(subscription)

    return subscription


@router.post("/create", response_model=dict)
async def create_subscription(
    request: CreateSubscriptionRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать подписку

    Перенаправляет на Stripe Checkout для оплаты
    """
    tier = request.tier.lower()

    if tier not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тариф: {tier}. Доступные: {', '.join(SUBSCRIPTION_PLANS.keys())}"
        )

    plan = SUBSCRIPTION_PLANS[tier]
    stripe_service = stripe_service

    # Проверяем существующую подписку
    existing_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()

    if existing_subscription and existing_subscription.status == SubscriptionStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас уже есть активная подписка"
        )

    # Создаём или получаем Stripe customer
    if not existing_subscription or not existing_subscription.stripe_customer_id:
        customer_result = stripe_service.create_customer(
            email=current_user.email,
            name=current_user.full_name,
            metadata={"user_id": current_user.id}
        )

        if "error" in customer_result and not customer_result.get("mock"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка создания клиента: {customer_result['error']}"
            )

        customer_id = customer_result.get("id")
    else:
        customer_id = existing_subscription.stripe_customer_id

    # Создаём Checkout сессию
    frontend_url = settings.FRONTEND_URL or "http://localhost:3000"
    success_url = f"{frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{frontend_url}/billing/cancel"
    
    # Price ID должен быть получен из Stripe (в production используем реальные ID)
    # Для demo используем заглушку
    price_id = f"price_{tier}_mock"  # В production: реальный price_id из Stripe
    
    checkout_result = stripe_service.create_checkout_session(
        customer_id=customer_id,
        price_id=price_id,
        success_url=success_url,
        cancel_url=cancel_url,
        mode="subscription",
        trial_period_days=plan.trial_days
    )

    if "error" in checkout_result and not checkout_result.get("mock"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания сессии: {checkout_result['error']}"
        )

    # Сохраняем информацию о подписке (будет активирована после webhook)
    if not existing_subscription:
        existing_subscription = Subscription(
            user_id=current_user.id,
            stripe_customer_id=customer_id,
            tier=getattr(SubscriptionTier, tier.upper()),
            status=SubscriptionStatus.TRIAL,
            amount=plan.price,
            currency=plan.currency,
        )
        db.add(existing_subscription)
    else:
        existing_subscription.stripe_customer_id = customer_id
        existing_subscription.tier = getattr(SubscriptionTier, tier.upper())
        existing_subscription.status = SubscriptionStatus.TRIAL
        existing_subscription.amount = plan.price
        existing_subscription.currency = plan.currency

    db.commit()

    return {
        "checkout_url": checkout_result["url"],
        "subscription_id": existing_subscription.id,
        "tier": tier,
        "trial_days": plan.trial_days,
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отменить подписку

    Подписка остаётся активной до конца оплаченного периода
    """
    stripe_service = stripe_service
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )

    if subscription.tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нечего отменять — у вас бесплатный тариф"
        )

    # Отменяем в Stripe
    if subscription.stripe_subscription_id:
        result = stripe_service.cancel_subscription(
            subscription.stripe_subscription_id,
            at_period_end=True
        )

        if "error" in result and not result.get("mock"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка отмены: {result['error']}"
            )

    # Обновляем локальную подписку
    subscription.cancel_at_period_end = True
    db.commit()

    return {
        "message": "Подписка будет отменена в конце периода",
        "current_period_end": subscription.current_period_end,
        "days_remaining": subscription.days_until_renewal,
    }


@router.delete("/cancel-now")
async def cancel_subscription_now(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отменить подписку немедленно

    Возвращает пропорциональную сумму за неиспользованный период
    """
    stripe_service = stripe_service
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )

    if subscription.tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нечего отменять — у вас бесплатный тариф"
        )

    # Отменяем в Stripe немедленно
    if subscription.stripe_subscription_id:
        result = stripe_service.cancel_subscription(
            subscription.stripe_subscription_id,
            at_period_end=False
        )

        if "error" in result and not result.get("mock"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка отмены: {result['error']}"
            )

    # Обновляем локальную подписку
    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = subscription.created_at
    db.commit()

    return {
        "message": "Подписка отменена немедленно",
        "refunded": True,
    }
