"""
Stripe Payment Service
Интеграция платежной системы Stripe
"""

import logging
import os
from decimal import Decimal
from typing import Any, Dict, Optional

try:
    import stripe

    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class StripeService:
    """Сервис для работы со Stripe API"""

    def __init__(self):
        """Инициализация Stripe"""
        # Mock mode для тестирования
        self.mock_mode = getattr(settings, 'STRIPE_MOCK_MODE', False) or \
                         os.environ.get('STRIPE_MOCK_MODE', '').lower() == 'true'

        if self.mock_mode:
            self.enabled = False
            self.mock_mode = True
            logger.info("Stripe running in MOCK mode for testing")
        elif STRIPE_AVAILABLE and settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            self.enabled = True
            logger.info("✅ Stripe API initialized")
        else:
            self.enabled = False
            if not STRIPE_AVAILABLE:
                logger.warning("⚠️ Stripe SDK not installed. Install: pip install stripe")
            else:
                logger.warning("⚠️ STRIPE_SECRET_KEY not configured")

    def create_payment_intent(
        self, amount: Decimal, currency: str = "usd", description: str = "", metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создать платежное намерение (Payment Intent)

        Args:
            amount: Сумма в основной валюте (например, 50.00 USD)
            currency: Код валюты (usd, eur, rub)
            description: Описание платежа
            metadata: Дополнительные данные

        Returns:
            Dict с информацией о Payment Intent
        """
        if not self.enabled:
            # Mock mode для тестирования - без хардкода client_secret
            if self.mock_mode:
                import uuid
                intent_id = f"pi_mock_{uuid.uuid4().hex[:16]}"
                return {
                    "error": "Stripe mock mode",
                    "mock": True,
                    "id": intent_id,
                    "client_secret": f"{intent_id}_secret",
                    "amount": float(amount),
                    "currency": currency,
                }
            return {
                "error": "Stripe not configured",
                "mock": True,
                "client_secret": "mock_secret_for_testing",
                "amount": float(amount),
                "currency": currency,
            }

        try:
            # Stripe работает в минимальных единицах (центы для USD)
            amount_cents = int(amount * 100)

            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                description=description,
                metadata=metadata or {},
                automatic_payment_methods={
                    "enabled": True,
                },
            )

            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "amount": amount_cents,
                "currency": intent.currency,
                "status": intent.status,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {"error": str(e), "type": e.__class__.__name__}
        except Exception as e:
            logger.error(f"Payment intent creation error: {e}")
            return {"error": "Internal server error"}

    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Подтвердить платеж

        Args:
            payment_intent_id: ID платежного намерения

        Returns:
            Dict с информацией о платеже
        """
        if not self.enabled:
            return {"mock": True, "status": "succeeded", "id": payment_intent_id}

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == "requires_confirmation":
                intent = stripe.PaymentIntent.confirm(payment_intent_id)

            return {
                "id": intent.id,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {"error": str(e), "type": e.__class__.__name__}

    def retrieve_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Получить информацию о платеже

        Args:
            payment_intent_id: ID платежного намерения

        Returns:
            Dict с информацией о платеже
        """
        if not self.enabled:
            return {"mock": True, "status": "succeeded", "id": payment_intent_id}

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            return {
                "id": intent.id,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
                "description": intent.description,
                "created": intent.created,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {"error": str(e), "type": e.__class__.__name__}

    def create_refund(
        self, payment_intent_id: str, amount: Optional[int] = None, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Создать возврат средств

        Args:
            payment_intent_id: ID платежного намерения
            amount: Сумма возврата (в центах), None = полный возврат
            reason: Причина возврата

        Returns:
            Dict с информацией о возврате
        """
        if not self.enabled:
            return {"mock": True, "status": "succeeded", "id": f"refund_{payment_intent_id}"}

        try:
            refund_data = {
                "payment_intent": payment_intent_id,
            }

            if amount:
                refund_data["amount"] = amount

            if reason:
                refund_data["reason"] = reason

            refund = stripe.Refund.create(**refund_data)

            return {
                "id": refund.id,
                "status": refund.status,
                "amount": refund.amount,
                "currency": refund.currency,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {"error": str(e), "type": e.__class__.__name__}

    def create_customer(
        self, email: str, name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создать клиента в Stripe

        Args:
            email: Email клиента
            name: Имя клиента
            metadata: Дополнительные данные

        Returns:
            Dict с информацией о клиенте
        """
        if not self.enabled:
            return {"mock": True, "id": f"cus_mock_{email}", "email": email}

        try:
            customer = stripe.Customer.create(email=email, name=name, metadata=metadata or {})

            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {"error": str(e), "type": e.__class__.__name__}

    def verify_webhook_signature(self, payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
        """
        Проверить подпись webhook от Stripe

        Args:
            payload: Тело запроса
            signature: Заголовок Stripe-Signature

        Returns:
            Event object если успешно, None если ошибка
        """
        if not self.enabled or not settings.STRIPE_WEBHOOK_SECRET:
            logger.warning("Webhook signature verification disabled")
            return None

        try:
            return stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)

        except ValueError:
            logger.error("Invalid webhook payload")
            return None
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return None

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_period_days: int = 14,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создать подписку

        Args:
            customer_id: ID клиента в Stripe
            price_id: ID тарифа в Stripe
            trial_period_days: Дней пробного периода
            metadata: Дополнительные данные

        Returns:
            Dict с информацией о подписке
        """
        if not self.enabled:
            return {
                "mock": True,
                "id": "sub_mock_123",
                "status": "trialing",
                "current_period_end": None,
            }

        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_period_days,
                metadata=metadata or {},
                automatic_tax={"enabled": True},
            )

            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "trial_end": subscription.trial_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription error: {e}")
            return {"error": str(e), "type": e.__class__.__name__}

    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Dict[str, Any]:
        """
        Отменить подписку

        Args:
            subscription_id: ID подписки
            at_period_end: Отменить в конце периода (True) или немедленно (False)

        Returns:
            Dict с информацией об отмене
        """
        if not self.enabled:
            return {"mock": True, "status": "cancelled"}

        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                return {
                    "id": subscription.id,
                    "status": subscription.status,
                    "cancel_at_period_end": True,
                    "current_period_end": subscription.current_period_end,
                }
            else:
                subscription = stripe.Subscription.cancel(subscription_id)
                return {
                    "id": subscription.id,
                    "status": subscription.status,
                    "cancelled_at": subscription.ended_at,
                }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe cancel error: {e}")
            return {"error": str(e), "type": e.__class__.__name__}

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Получить информацию о подписке

        Args:
            subscription_id: ID подписки

        Returns:
            Dict с информацией о подписке
        """
        if not self.enabled:
            return {"mock": True, "id": subscription_id, "status": "active"}

        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "items": [{"price": item.price.id} for item in subscription.items.data],
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe retrieve error: {e}")
            return {"error": str(e), "type": e.__class__.__name__}

    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
        trial_period_days: int = 14
    ) -> Dict[str, Any]:
        """
        Создать сессию Checkout для оплаты

        Args:
            customer_id: ID клиента
            price_id: ID тарифа
            success_url: URL успешной оплаты
            cancel_url: URL отмены
            mode: Режим (subscription или payment)
            trial_period_days: Дней пробного периода

        Returns:
            Dict с URL Checkout сессии
        """
        if not self.enabled:
            return {
                "mock": True,
                "url": "https://checkout.stripe.com/mock",
                "id": "checkout_mock_123",
            }

        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                mode=mode,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={
                    "trial_period_days": trial_period_days,
                } if mode == "subscription" else None,
            )

            return {
                "id": session.id,
                "url": session.url,
                "status": session.status,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe checkout error: {e}")
            return {"error": str(e), "type": e.__class__.__name__}


# Singleton instance
stripe_service = StripeService()
