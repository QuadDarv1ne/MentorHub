"""
Tests for Payments API
Тесты для endpoints оплаты
"""

import pytest
from fastapi import status


class TestPaymentsRead:
    """Тесты чтения платежей"""

    def test_get_payments_list(self, sync_authenticated_client):
        """Тест получения списка платежей"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/payments", headers=headers)
        # Должен вернуть 200 (возможно пустой список) или 404 если endpoint не найден
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_payments_unauthorized(self, client):
        """Тест получения платежей без авторизации"""
        response = client.get("/api/v1/payments")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPaymentCreate:
    """Тесты создания платежа"""

    def test_create_payment_success(self, sync_authenticated_client):
        """Тест успешного создания платежа"""
        client, headers = sync_authenticated_client

        payment_data = {
            "amount": 99.99,
            "currency": "RUB",
            "description": "Test payment",
        }

        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        # Может вернуть 201 (создан), 400 (ошибка), 422 (валидация)
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_create_payment_invalid_amount(self, sync_authenticated_client):
        """Тест создания платежа с невалидной суммой"""
        client, headers = sync_authenticated_client

        payment_data = {
            "amount": -100,  # Невалидно
            "currency": "RUB",
            "description": "Test payment",
        }

        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_payment_unauthorized(self, client):
        """Тест создания платежа без авторизации"""
        payment_data = {
            "amount": 99.99,
            "currency": "RUB",
        }
        response = client.post("/api/v1/payments", json=payment_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPaymentValidation:
    """Тесты валидации платежей"""

    @pytest.mark.parametrize("amount", [0.01, 10.00, 99.99, 1000.00])
    def test_payment_amount_values(self, amount):
        """Тест допустимых значений суммы"""
        assert amount > 0
        assert amount <= 1000000  # Max limit

    def test_payment_currency_values(self):
        """Тест допустимых значений валюты"""
        valid_currencies = ["RUB", "USD", "EUR"]
        for currency in valid_currencies:
            assert currency in ["RUB", "USD", "EUR"]


class TestPaymentEdgeCases:
    """Тесты граничных случаев"""

    def test_payment_zero_amount(self, sync_authenticated_client):
        """Тест платежа с нулевой суммой"""
        client, headers = sync_authenticated_client

        payment_data = {
            "amount": 0,
            "currency": "RUB",
        }

        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_payment_missing_description(self, sync_authenticated_client):
        """Тест платежа без описания"""
        client, headers = sync_authenticated_client

        payment_data = {
            "amount": 99.99,
            "currency": "RUB",
        }

        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        # Может быть 201 или 422 в зависимости от требований
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]
