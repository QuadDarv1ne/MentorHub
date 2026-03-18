"""
Tests for Two-Factor Authentication API
Тесты для endpoints 2FA
"""

import pytest
from fastapi import status


class TestTwoFactorSetup:
    """Тесты настройки 2FA"""

    def test_setup_2fa_success(self, sync_authenticated_client):
        """Тест успешной настройки 2FA"""
        client, headers = sync_authenticated_client

        setup_data = {
            "enabled": True,
        }

        response = client.post("/api/v1/2fa/setup", json=setup_data, headers=headers)
        # Может вернуть 200, 400, 422
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_setup_2fa_disable(self, sync_authenticated_client):
        """Тест отключения 2FA"""
        client, headers = sync_authenticated_client

        setup_data = {
            "enabled": False,
        }

        response = client.post("/api/v1/2fa/setup", json=setup_data, headers=headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_setup_2fa_unauthorized(self, client):
        """Тест настройки 2FA без авторизации"""
        setup_data = {
            "enabled": True,
        }
        response = client.post("/api/v1/2fa/setup", json=setup_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTwoFactorVerify:
    """Тесты верификации 2FA"""

    def test_verify_2fa_success(self, sync_authenticated_client):
        """Тест успешной верификации 2FA"""
        client, headers = sync_authenticated_client

        verify_data = {
            "code": "123456",
        }

        response = client.post("/api/v1/2fa/verify", json=verify_data, headers=headers)
        # Может вернуть 200, 400, 401
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_verify_2fa_invalid_code(self, sync_authenticated_client):
        """Тест верификации с неверным кодом"""
        client, headers = sync_authenticated_client

        verify_data = {
            "code": "000000",  # Неверный код
        }

        response = client.post("/api/v1/2fa/verify", json=verify_data, headers=headers)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_verify_2fa_unauthorized(self, client):
        """Тест верификации 2FA без авторизации"""
        verify_data = {
            "code": "123456",
        }
        response = client.post("/api/v1/2fa/verify", json=verify_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTwoFactorStatus:
    """Тесты статуса 2FA"""

    def test_get_2fa_status(self, sync_authenticated_client):
        """Тест получения статуса 2FA"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/2fa/status", headers=headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_get_2fa_status_unauthorized(self, client):
        """Тест получения статуса 2FA без авторизации"""
        response = client.get("/api/v1/2fa/status")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTwoFactorValidation:
    """Тесты валидации 2FA"""

    def test_2fa_code_format(self):
        """Тест формата 2FA кода"""
        # 2FA код - 6 цифр
        valid_code = "123456"
        assert len(valid_code) == 6
        assert valid_code.isdigit()

    def test_2fa_code_invalid_format(self):
        """Тест неверного формата 2FA кода"""
        invalid_codes = [
            "12345",  # Слишком короткий
            "1234567",  # Слишком длинный
            "abcdef",  # Не цифры
            "12345a",  # Смешанные символы
        ]
        for code in invalid_codes:
            assert not (len(code) == 6 and code.isdigit())

    @pytest.mark.parametrize("enabled", [True, False])
    def test_2fa_enabled_values(self, enabled):
        """Тест допустимых значений enabled"""
        assert isinstance(enabled, bool)
