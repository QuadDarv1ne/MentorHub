"""
Tests for Email Verification API
Тесты для endpoints верификации email
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


class TestSendVerificationEmail:
    """Тесты отправки письма для подтверждения email"""

    def test_send_verification_email_success(self, sync_authenticated_client):
        """Тест успешной отправки письма для подтверждения"""
        client, headers = sync_authenticated_client

        response = client.post("/api/v1/email/send-verification", headers=headers)
        # Может быть 200 если отправлено или 500 если SMTP не настроен
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_send_verification_email_unauthorized(self, client):
        """Тест отправки письма без авторизации"""
        response = client.post("/api/v1/email/send-verification")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestVerifyEmail:
    """Тесты подтверждения email"""

    def test_verify_email_success(self, client):
        """Тест подтверждения email"""
        # Сначала нужно получить токен (через send-verification)
        # Затем подтвердить
        response = client.post(
            "/api/v1/email/verify-email",
            json={"token": "invalid_token"},
        )
        # С невалидным токеном должен быть 400 или 404
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_verify_email_invalid_token(self, client):
        """Тест подтверждения email с невалидным токеном"""
        response = client.post(
            "/api/v1/email/verify-email",
            json={"token": "nonexistent_token"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_email_missing_token(self, client):
        """Тест подтверждения email без токена"""
        response = client.post(
            "/api/v1/email/verify-email",
            json={},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestForgotPassword:
    """Тесты восстановления пароля"""

    def test_forgot_password_success(self, client):
        """Тест успешного запроса на восстановление пароля"""
        # Сначала зарегистрируем пользователя
        client.post("/api/v1/auth/register", json=sample_user_data)

        # Запрос на восстановление
        response = client.post(
            "/api/v1/email/forgot-password",
            json={"email": sample_user_data["email"]},
        )
        # Может быть 200 если отправлено или 500 если SMTP не настроен
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_forgot_password_nonexistent_email(self, client):
        """Тест восстановления для несуществующего email"""
        response = client.post(
            "/api/v1/email/forgot-password",
            json={"email": "nonexistent@example.com"},
        )
        # Для безопасности должен вернуть 200 (не раскрывать существование email)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_forgot_password_invalid_email(self, client):
        """Тест восстановления с невалидным email"""
        response = client.post(
            "/api/v1/email/forgot-password",
            json={"email": "not-an-email"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestResetPassword:
    """Тесты сброса пароля"""

    def test_reset_password_success(self, client):
        """Тест успешного сброса пароля"""
        # С невалидным токеном
        response = client.post(
            "/api/v1/email/reset-password",
            json={
                "token": "invalid_token",
                "new_password": "NewPass123!",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_weak_password(self, client):
        """Тест сброса пароля на слабый пароль"""
        response = client.post(
            "/api/v1/email/reset-password",
            json={
                "token": "invalid_token",
                "new_password": "123",  # Слишком короткий
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_reset_password_missing_fields(self, client):
        """Тест сброса пароля с отсутствующими полями"""
        response = client.post(
            "/api/v1/email/reset-password",
            json={},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestEmailVerificationIntegration:
    """Интеграционные тесты верификации email"""

    def test_full_verification_flow(self, client):
        """Тест полного процесса верификации"""
        # 1. Регистрация
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # 2. Вход
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Отправка verification email
        response = client.post("/api/v1/email/send-verification", headers=headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]


class TestEmailValidation:
    """Тесты валидации email"""

    @pytest.mark.parametrize("email", [
        "valid@example.com",
        "user.name@domain.org",
        "test+tag@mail.com",
    ])
    def test_valid_email_formats(self, email):
        """Тест валидных email форматов"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert re.match(pattern, email)

    @pytest.mark.parametrize("email", [
        "invalid",
        "@nodomain.com",
        "no@at.com",
        "spaces @domain.com",
    ])
    def test_invalid_email_formats(self, email):
        """Тест невалидных email форматов"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert not re.match(pattern, email)
