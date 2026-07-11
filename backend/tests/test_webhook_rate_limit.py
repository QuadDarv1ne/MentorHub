"""
Tests for webhook rate limiter
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, Request, status

from app.dependencies import _webhook_rate_limiter, webhook_rate_limit_dependency


class TestWebhookRateLimiter:
    """Тесты для webhook rate limiter"""

    @pytest.fixture
    def mock_request(self):
        """Создание mock запроса"""
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.100"
        request.url.path = "/api/payments/webhook"
        return request

    def test_webhook_rate_limit_allows_first_requests(self, mock_request):
        """Тест: первые запросы проходят"""
        # Проверяем что rate limiter существует
        assert _webhook_rate_limiter is not None

        # Первые 500 запросов должны проходить
        for _ in range(10):
            result = webhook_rate_limit_dependency(mock_request)
            assert result is True

    def test_webhook_rate_limit_blocks_excess_requests(self, mock_request):
        """Тест: запросы сверх лимита блокируются"""
        # Превышаем лимит в 500 запросов
        for _ in range(500):
            webhook_rate_limit_dependency(mock_request)

        # 501-й запрос должен быть заблокирован
        with pytest.raises(HTTPException) as exc_info:
            webhook_rate_limit_dependency(mock_request)

        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Webhook rate limit exceeded" in exc_info.value.detail

    def test_webhook_rate_limit_uses_ip_and_path(self, mock_request):
        """Тест: rate limiter использует IP и path для идентификации"""
        # Первый запрос
        result1 = webhook_rate_limit_dependency(mock_request)
        assert result1 is True

        # Запрос с другого IP должен пройти
        mock_request2 = MagicMock(spec=Request)
        mock_request2.client.host = "192.168.1.101"
        mock_request2.url.path = "/api/payments/webhook"

        result2 = webhook_rate_limit_dependency(mock_request2)
        assert result2 is True

        # Запрос на другой путь должен пройти
        mock_request3 = MagicMock(spec=Request)
        mock_request3.client.host = "192.168.1.100"
        mock_request3.url.path = "/api/payments/sbp/webhook"

        result3 = webhook_rate_limit_dependency(mock_request3)
        assert result3 is True

    def test_webhook_rate_limit_when_disabled(self):
        """Тест: когда rate limiter отключен, все запросы проходят"""
        with patch('app.dependencies._webhook_rate_limiter', None):
            mock_request = MagicMock(spec=Request)
            mock_request.client.host = "192.168.1.100"
            mock_request.url.path = "/api/payments/webhook"

            result = webhook_rate_limit_dependency(mock_request)
            assert result is True

    def test_webhook_rate_limit_with_missing_client(self):
        """Тест: обработка запроса без client информации"""
        mock_request = MagicMock(spec=Request)
        mock_request.client = None
        mock_request.url.path = "/api/payments/webhook"

        # Должно использовать "unknown" как IP
        result = webhook_rate_limit_dependency(mock_request)
        assert result is True
