"""
Mock Stripe Service для тестирования
Используется только в тестовом окружении
"""

import logging
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)


class MockStripeService:
    """Mock сервис для Stripe API - используется только в тестах"""

    def __init__(self):
        """Инициализация mock сервиса"""
        self.enabled = True
        self.payment_intents = {}
        self.customers = {}
        self.subscriptions = {}
        self.refunds = {}
        logger.info("MockStripeService initialized for testing")

    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str = "usd",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Создать mock платежное намерение"""
        intent_id = f"pi_mock_{uuid.uuid4().hex[:16]}"
        client_secret = f"{intent_id}_secret_{uuid.uuid4().hex[:8]}"

        payment_intent = {
            "id": intent_id,
            "client_secret": client_secret,
            "amount": int(amount * 100),
            "currency": currency,
            "status": "requires_confirmation",
            "description": description,
            "metadata": metadata or {},
        }

        self.payment_intents[intent_id] = payment_intent

        return {
            "id": intent_id,
            "client_secret": client_secret,
            "amount": int(amount * 100),
            "currency": currency,
            "status": "requires_confirmation",
        }

    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Подтвердить mock платеж"""
        if payment_intent_id not in self.payment_intents:
            return {"error": "Payment intent not found", "type": "InvalidRequestError"}

        intent = self.payment_intents[payment_intent_id]
        intent["status"] = "succeeded"

        return {
            "id": intent["id"],
            "status": "succeeded",
            "amount": intent["amount"],
            "currency": intent["currency"],
        }

    def retrieve_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Получить информацию о mock платеже"""
        if payment_intent_id not in self.payment_intents:
            return {"error": "Payment intent not found", "type": "InvalidRequestError"}

        intent = self.payment_intents[payment_intent_id]

        return {
            "id": intent["id"],
            "status": intent["status"],
            "amount": intent["amount"],
            "currency": intent["currency"],
            "description": intent.get("description", ""),
            "created": 1234567890,
        }

    def create_refund(
        self,
        payment_intent_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Создать mock возврат"""
        refund_id = f"re_mock_{uuid.uuid4().hex[:16]}"

        refund = {
            "id": refund_id,
            "payment_intent_id": payment_intent_id,
            "amount": amount,
            "reason": reason,
            "status": "succeeded",
        }

        self.refunds[refund_id] = refund

        return {
            "id": refund_id,
            "status": "succeeded",
            "amount": amount,
            "currency": "usd",
        }

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Создать mock клиента"""
        customer_id = f"cus_mock_{uuid.uuid4().hex[:8]}"

        customer = {
            "id": customer_id,
            "email": email,
            "name": name,
            "metadata": metadata or {},
        }

        self.customers[customer_id] = customer

        return {
            "id": customer_id,
            "email": email,
            "name": name,
        }

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> Optional[Dict[str, Any]]:
        """Проверить подпись mock webhook (всегда успешно в тестах)"""
        logger.warning("Mock webhook signature verification - always succeeds")
        return {"type": "mock_event", "data": {"object": {}}}

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_period_days: int = 14,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Создать mock подписку"""
        subscription_id = f"sub_mock_{uuid.uuid4().hex[:16]}"

        subscription = {
            "id": subscription_id,
            "customer_id": customer_id,
            "price_id": price_id,
            "status": "trialing",
            "trial_period_days": trial_period_days,
            "metadata": metadata or {},
        }

        self.subscriptions[subscription_id] = subscription

        return {
            "id": subscription_id,
            "status": "trialing",
            "current_period_start": 1234567890,
            "current_period_end": 1234567890 + (trial_period_days * 86400),
            "trial_end": 1234567890 + (trial_period_days * 86400),
            "cancel_at_period_end": False,
        }

    def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True
    ) -> Dict[str, Any]:
        """Отменить mock подписку"""
        if subscription_id not in self.subscriptions:
            return {"error": "Subscription not found", "type": "InvalidRequestError"}

        subscription = self.subscriptions[subscription_id]

        if at_period_end:
            subscription["cancel_at_period_end"] = True
            return {
                "id": subscription_id,
                "status": subscription["status"],
                "cancel_at_period_end": True,
                "current_period_end": subscription["current_period_end"],
            }
        else:
            subscription["status"] = "canceled"
            return {
                "id": subscription_id,
                "status": "canceled",
                "cancelled_at": 1234567890,
            }

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Получить информацию о mock подписке"""
        if subscription_id not in self.subscriptions:
            return {"error": "Subscription not found", "type": "InvalidRequestError"}

        subscription = self.subscriptions[subscription_id]

        return {
            "id": subscription["id"],
            "status": subscription["status"],
            "current_period_start": subscription.get("current_period_start", 1234567890),
            "current_period_end": subscription.get("current_period_end", 1234567890),
            "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
            "items": [{"price": subscription.get("price_id", "")}],
        }

    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
        trial_period_days: int = 14
    ) -> Dict[str, Any]:
        """Создать mock checkout сессию"""
        session_id = f"cs_mock_{uuid.uuid4().hex[:16]}"

        return {
            "id": session_id,
            "url": f"https://checkout.stripe.com/mock/{session_id}",
            "status": "open",
        }

    # Методы для тестов
    def clear_all_data(self):
        """Очистить все mock данные (для тестов)"""
        self.payment_intents.clear()
        self.customers.clear()
        self.subscriptions.clear()
        self.refunds.clear()
        logger.debug("MockStripeService data cleared")

    def get_payment_intent(self, payment_intent_id: str) -> Optional[Dict[str, Any]]:
        """Получить mock payment intent из хранилища"""
        return self.payment_intents.get(payment_intent_id)

    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Получить mock customer из хранилища"""
        return self.customers.get(customer_id)

    def get_subscription_data(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Получить mock subscription из хранилища"""
        return self.subscriptions.get(subscription_id)


# Singleton instance для тестов
mock_stripe_service = MockStripeService()
