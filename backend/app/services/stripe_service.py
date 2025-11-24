"""
Stripe Payment Service
Интеграция платежной системы Stripe
"""

import logging
from typing import Optional, Dict, Any
from decimal import Decimal

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
        if STRIPE_AVAILABLE and settings.STRIPE_SECRET_KEY:
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
        self,
        amount: Decimal,
        currency: str = "usd",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
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
            return {
                "error": "Stripe not configured",
                "mock": True,
                "client_secret": "mock_secret_for_testing",
                "amount": float(amount),
                "currency": currency
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
                    'enabled': True,
                }
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
            return {
                "error": str(e),
                "type": e.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Payment intent creation error: {e}")
            return {
                "error": "Internal server error"
            }
    
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Подтвердить платеж
        
        Args:
            payment_intent_id: ID платежного намерения
            
        Returns:
            Dict с информацией о платеже
        """
        if not self.enabled:
            return {
                "mock": True,
                "status": "succeeded",
                "id": payment_intent_id
            }
        
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
            return {
                "error": str(e),
                "type": e.__class__.__name__
            }
    
    def retrieve_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Получить информацию о платеже
        
        Args:
            payment_intent_id: ID платежного намерения
            
        Returns:
            Dict с информацией о платеже
        """
        if not self.enabled:
            return {
                "mock": True,
                "status": "succeeded",
                "id": payment_intent_id
            }
        
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
            return {
                "error": str(e),
                "type": e.__class__.__name__
            }
    
    def create_refund(
        self,
        payment_intent_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None
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
            return {
                "mock": True,
                "status": "succeeded",
                "id": f"refund_{payment_intent_id}"
            }
        
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
            return {
                "error": str(e),
                "type": e.__class__.__name__
            }
    
    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
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
            return {
                "mock": True,
                "id": f"cus_mock_{email}",
                "email": email
            }
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {
                "error": str(e),
                "type": e.__class__.__name__
            }
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> Optional[Dict[str, Any]]:
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
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        
        except ValueError:
            logger.error("Invalid webhook payload")
            return None
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return None


# Singleton instance
stripe_service = StripeService()
