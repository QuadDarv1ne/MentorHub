"""
Сервис интеграции с СБП (Система быстрых платежей)
Поддерживает создание QR-кодов, проверку статуса платежей и возвраты
"""

import logging
from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import hashlib
import json
from app.config import settings

logger = logging.getLogger(__name__)

# Проверка доступности библиотеки requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("⚠️ requests library not installed. Install: pip install requests")


class SBPService:
    """
    Сервис для работы с СБП API
    
    Поддерживаемые операции:
    - Создание QR-кода для оплаты
    - Проверка статуса платежа
    - Возврат средств
    - Получение информации о банках СБП
    """
    
    def __init__(self):
        """Инициализация сервиса СБП"""
        self.enabled = False
        self.merchant_id = getattr(settings, 'SBP_MERCHANT_ID', None)
        self.api_key = getattr(settings, 'SBP_API_KEY', None)
        self.secret_key = getattr(settings, 'SBP_SECRET_KEY', None)
        self.base_url = getattr(settings, 'SBP_API_URL', 'https://api.sbp.ru/v1')
        
        if REQUESTS_AVAILABLE and self.merchant_id and self.api_key:
            self.enabled = True
            logger.info("✅ SBP service initialized successfully")
        else:
            logger.warning("⚠️ SBP service running in MOCK mode")
    
    def _generate_signature(self, data: Dict) -> str:
        """
        Генерация подписи для запроса к СБП API
        
        Args:
            data: Данные запроса
            
        Returns:
            Подпись запроса
        """
        if not self.secret_key:
            return "mock_signature"
        
        # Сортируем ключи для консистентности
        sorted_data = sorted(data.items())
        message = ''.join([f"{k}={v}" for k, v in sorted_data])
        message += self.secret_key
        
        signature = hashlib.sha256(message.encode()).hexdigest()
        return signature
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Выполнение HTTP запроса к СБП API
        
        Args:
            method: HTTP метод (GET, POST)
            endpoint: Эндпоинт API
            data: Данные запроса
            
        Returns:
            Ответ API
        """
        if not self.enabled:
            logger.warning("SBP API request in MOCK mode")
            return {"error": "SBP not configured"}
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            if method.upper() == "POST":
                if data:
                    data['signature'] = self._generate_signature(data)
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"SBP API request failed: {str(e)}")
            return {"error": str(e)}
    
    def create_qr_code(
        self,
        amount: Decimal,
        description: str = "",
        order_id: str = "",
        customer_phone: Optional[str] = None,
        ttl_minutes: int = 15
    ) -> Dict:
        """
        Создание QR-кода для оплаты через СБП
        
        Args:
            amount: Сумма платежа в рублях
            description: Описание платежа
            order_id: ID заказа в системе
            customer_phone: Номер телефона клиента (опционально)
            ttl_minutes: Время жизни QR-кода в минутах
            
        Returns:
            Данные QR-кода и платежа
        """
        logger.info(f"Creating SBP QR code: amount={amount}, order_id={order_id}")
        
        if not self.enabled:
            # Mock режим
            mock_qr_id = f"sbp_qr_mock_{order_id}_{datetime.utcnow().timestamp()}"
            logger.warning(f"MOCK MODE: SBP QR code created - {mock_qr_id}")
            
            return {
                "qr_id": mock_qr_id,
                "qr_url": f"https://qr.nspk.ru/{mock_qr_id}",
                "qr_image": f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "amount": float(amount),
                "status": "pending",
                "expires_at": (datetime.utcnow() + timedelta(minutes=ttl_minutes)).isoformat(),
                "order_id": order_id,
            }
        
        # Реальный запрос к СБП API
        request_data = {
            "merchant_id": self.merchant_id,
            "amount": int(amount * 100),  # В копейках
            "currency": "RUB",
            "order_id": order_id,
            "description": description or f"Оплата заказа {order_id}",
            "ttl": ttl_minutes,
        }
        
        if customer_phone:
            request_data["customer_phone"] = customer_phone
        
        try:
            response = self._make_request("POST", "qr/create", request_data)
            
            if "error" in response:
                logger.error(f"Failed to create SBP QR: {response['error']}")
                return response
            
            logger.info(f"SBP QR code created: {response.get('qr_id')}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating SBP QR code: {str(e)}")
            return {"error": str(e)}
    
    def check_payment_status(self, qr_id: str) -> Dict:
        """
        Проверка статуса платежа по QR-коду
        
        Args:
            qr_id: ID QR-кода
            
        Returns:
            Статус платежа
        """
        logger.info(f"Checking SBP payment status: qr_id={qr_id}")
        
        if not self.enabled:
            # Mock режим - имитируем успешный платеж
            logger.warning(f"MOCK MODE: SBP payment status check - {qr_id}")
            
            return {
                "qr_id": qr_id,
                "status": "completed",
                "amount": 5000,  # 50 рублей
                "transaction_id": f"sbp_txn_mock_{datetime.utcnow().timestamp()}",
                "bank_name": "Сбербанк",
                "completed_at": datetime.utcnow().isoformat(),
            }
        
        # Реальный запрос к СБП API
        try:
            response = self._make_request("GET", f"qr/{qr_id}/status")
            
            if "error" in response:
                logger.error(f"Failed to check SBP status: {response['error']}")
                return response
            
            logger.info(f"SBP payment status: {response.get('status')}")
            return response
        
        except Exception as e:
            logger.error(f"Error checking SBP payment status: {str(e)}")
            return {"error": str(e)}
    
    def create_refund(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "requested_by_customer"
    ) -> Dict:
        """
        Создание возврата средств через СБП
        
        Args:
            transaction_id: ID транзакции
            amount: Сумма возврата (если None - полный возврат)
            reason: Причина возврата
            
        Returns:
            Данные возврата
        """
        logger.info(f"Creating SBP refund: transaction_id={transaction_id}, amount={amount}")
        
        if not self.enabled:
            # Mock режим
            mock_refund_id = f"sbp_refund_mock_{datetime.utcnow().timestamp()}"
            logger.warning(f"MOCK MODE: SBP refund created - {mock_refund_id}")
            
            return {
                "refund_id": mock_refund_id,
                "transaction_id": transaction_id,
                "status": "completed",
                "amount": float(amount) if amount else 5000,
                "reason": reason,
                "created_at": datetime.utcnow().isoformat(),
            }
        
        # Реальный запрос к СБП API
        request_data = {
            "merchant_id": self.merchant_id,
            "transaction_id": transaction_id,
            "reason": reason,
        }
        
        if amount:
            request_data["amount"] = int(amount * 100)  # В копейках
        
        try:
            response = self._make_request("POST", "refunds/create", request_data)
            
            if "error" in response:
                logger.error(f"Failed to create SBP refund: {response['error']}")
                return response
            
            logger.info(f"SBP refund created: {response.get('refund_id')}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating SBP refund: {str(e)}")
            return {"error": str(e)}
    
    def get_available_banks(self) -> Dict:
        """
        Получение списка банков, поддерживающих СБП
        
        Returns:
            Список банков
        """
        logger.info("Fetching available SBP banks")
        
        if not self.enabled:
            # Mock режим - популярные банки
            logger.warning("MOCK MODE: Returning mock SBP banks list")
            
            return {
                "banks": [
                    {"id": "100000000111", "name": "Сбербанк", "logo_url": "https://example.com/sber.png"},
                    {"id": "100000000004", "name": "Тинькофф Банк", "logo_url": "https://example.com/tinkoff.png"},
                    {"id": "100000000015", "name": "ВТБ", "logo_url": "https://example.com/vtb.png"},
                    {"id": "100000000008", "name": "Альфа-Банк", "logo_url": "https://example.com/alfa.png"},
                    {"id": "100000000012", "name": "Райффайзенбанк", "logo_url": "https://example.com/raif.png"},
                ]
            }
        
        # Реальный запрос к СБП API
        try:
            response = self._make_request("GET", "banks")
            
            if "error" in response:
                logger.error(f"Failed to fetch SBP banks: {response['error']}")
                return response
            
            logger.info(f"Fetched {len(response.get('banks', []))} SBP banks")
            return response
        
        except Exception as e:
            logger.error(f"Error fetching SBP banks: {str(e)}")
            return {"error": str(e)}
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> Optional[Dict]:
        """
        Проверка подписи webhook от СБП
        
        Args:
            payload: Тело запроса
            signature: Подпись из заголовка
            
        Returns:
            Данные события или None если подпись невалидна
        """
        if not self.secret_key:
            logger.warning("MOCK MODE: Webhook signature verification skipped")
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return None
        
        try:
            # Вычисляем ожидаемую подпись
            expected_signature = hashlib.sha256(
                payload + self.secret_key.encode()
            ).hexdigest()
            
            if expected_signature != signature:
                logger.error("Invalid SBP webhook signature")
                return None
            
            logger.info("SBP webhook signature verified")
            return json.loads(payload)
        
        except Exception as e:
            logger.error(f"Error verifying SBP webhook signature: {str(e)}")
            return None


# Singleton instance
sbp_service = SBPService()
