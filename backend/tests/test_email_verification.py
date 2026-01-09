"""
Тесты для email верификации и восстановления пароля
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from datetime import datetime, timedelta

from app.models.user import User, UserRole
from app.utils.security import get_password_hash
from app.utils.email import EmailService


class TestEmailVerification:
    """Тесты для email верификации"""

    def test_send_verification_email_success(self, client, db_session, sample_user_data):
        """Тест успешной отправки письма верификации"""
        # Регистрация пользователя
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Отправка письма верификации
        email_data = {"email": sample_user_data["email"]}
        response = client.post("/api/v1/email/send-verification", json=email_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "expires_in_hours" in data

    def test_send_verification_email_nonexistent_user(self, client):
        """Тест отправки письма несуществующему пользователю"""
        email_data = {"email": "nonexistent@example.com"}
        response = client.post("/api/v1/email/send-verification", json=email_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_verify_email_success(self, client, db_session, sample_user_data):
        """Тест успешной верификации email"""
        # Регистрация пользователя
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        user = db_session.query(User).filter(User.email == sample_user_data["email"]).first()
        assert user is not None
        assert user.is_verified is False
        
        # Создание токена верификации (имитация)
        with patch('app.utils.security.generate_verification_token') as mock_token:
            mock_token.return_value = "test_verification_token"
            
            # Отправка письма верификации
            email_data = {"email": sample_user_data["email"]}
            client.post("/api/v1/email/send-verification", json=email_data)
            
            # Верификация email
            verify_data = {"token": "test_verification_token"}
            response = client.post("/api/v1/email/verify-email", json=verify_data)
            
            assert response.status_code == status.HTTP_200_OK
            
            # Проверка что пользователь теперь верифицирован
            db_session.refresh(user)
            assert user.is_verified is True

    def test_verify_email_invalid_token(self, client):
        """Тест верификации с неверным токеном"""
        verify_data = {"token": "invalid_token"}
        response = client.post("/api/v1/email/verify-email", json=verify_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_email_expired_token(self, client, db_session, sample_user_data):
        """Тест верификации с истекшим токеном"""
        # Регистрация пользователя
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Создание истекшего токена
        with patch('app.utils.security.decode_verification_token') as mock_decode:
            mock_decode.side_effect = Exception("Token expired")
            
            verify_data = {"token": "expired_token"}
            response = client.post("/api/v1/email/verify-email", json=verify_data)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPasswordReset:
    """Тесты для восстановления пароля"""

    def test_forgot_password_success(self, client, db_session, sample_user_data):
        """Тест успешного запроса восстановления пароля"""
        # Регистрация пользователя
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Запрос восстановления пароля
        email_data = {"email": sample_user_data["email"]}
        response = client.post("/api/v1/email/forgot-password", json=email_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "expires_in_hours" in data

    def test_forgot_password_nonexistent_user(self, client):
        """Тест восстановления пароля для несуществующего пользователя"""
        email_data = {"email": "nonexistent@example.com"}
        response = client.post("/api/v1/email/forgot-password", json=email_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_reset_password_success(self, client, db_session, sample_user_data):
        """Тест успешного сброса пароля"""
        # Регистрация пользователя
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        user = db_session.query(User).filter(User.email == sample_user_data["email"]).first()
        old_hashed_password = user.hashed_password
        
        # Создание токена сброса (имитация)
        with patch('app.utils.security.generate_verification_token') as mock_token:
            mock_token.return_value = "test_reset_token"
            
            # Запрос восстановления пароля
            email_data = {"email": sample_user_data["email"]}
            client.post("/api/v1/email/forgot-password", json=email_data)
            
            # Сброс пароля
            reset_data = {
                "token": "test_reset_token",
                "new_password": "new_secure_password123"
            }
            response = client.post("/api/v1/email/reset-password", json=reset_data)
            
            assert response.status_code == status.HTTP_200_OK
            
            # Проверка что пароль действительно изменился
            db_session.refresh(user)
            assert user.hashed_password != old_hashed_password

    def test_reset_password_invalid_token(self, client):
        """Тест сброса пароля с неверным токеном"""
        reset_data = {
            "token": "invalid_token",
            "new_password": "new_password123"
        }
        response = client.post("/api/v1/email/reset-password", json=reset_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_weak_password(self, client, sample_user_data):
        """Тест сброса пароля со слабым паролем"""
        reset_data = {
            "token": "valid_token",
            "new_password": "123"  # Слишком короткий
        }
        response = client.post("/api/v1/email/reset-password", json=reset_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestEmailService:
    """Тесты для EmailService"""

    @patch('app.utils.email.smtplib.SMTP')
    async def test_send_verification_email(self, mock_smtp):
        """Тест отправки письма верификации"""
        # Настройка мока
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Тестовые данные
        email_service = EmailService()
        to_email = "test@example.com"
        username = "testuser"
        verification_token = "test_token"
        
        # Вызов метода
        await email_service.send_verification_email(to_email, username, verification_token)
        
        # Проверки
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()

    @patch('app.utils.email.smtplib.SMTP')
    async def test_send_password_reset_email(self, mock_smtp):
        """Тест отправки письма восстановления пароля"""
        # Настройка мока
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Тестовые данные
        email_service = EmailService()
        to_email = "test@example.com"
        username = "testuser"
        reset_token = "reset_token"
        
        # Вызов метода
        await email_service.send_password_reset_email(to_email, username, reset_token)
        
        # Проверки
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()


@pytest.mark.integration
class TestEmailIntegration:
    """Интеграционные тесты для email функциональности"""

    def test_full_verification_flow(self, client, db_session, sample_user_data):
        """Тест полного процесса верификации: регистрация -> отправка письма -> верификация"""
        # 1. Регистрация
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # 2. Проверка что пользователь не верифицирован
        user = db_session.query(User).filter(User.email == sample_user_data["email"]).first()
        assert user.is_verified is False
        
        # 3. Отправка письма верификации
        with patch('app.tasks.celery_tasks.send_verification_email_task.delay') as mock_task:
            email_response = client.post(
                "/api/v1/email/send-verification", 
                json={"email": sample_user_data["email"]}
            )
            assert email_response.status_code == status.HTTP_200_OK
            mock_task.assert_called_once()
        
        # 4. Верификация (с мокнутым токеном)
        with patch('app.utils.security.decode_verification_token') as mock_decode:
            mock_decode.return_value = {"sub": str(user.id), "email": user.email}
            
            verify_response = client.post(
                "/api/v1/email/verify-email",
                json={"token": "mock_token"}
            )
            assert verify_response.status_code == status.HTTP_200_OK
        
        # 5. Проверка что пользователь теперь верифицирован
        db_session.refresh(user)
        assert user.is_verified is True

    def test_password_reset_flow(self, client, db_session, sample_user_data):
        """Тест полного процесса сброса пароля"""
        # 1. Регистрация
        client.post("/api/v1/auth/register", json=sample_user_data)
        user = db_session.query(User).filter(User.email == sample_user_data["email"]).first()
        old_password_hash = user.hashed_password
        
        # 2. Запрос восстановления пароля
        with patch('app.tasks.celery_tasks.send_password_reset_email_task.delay') as mock_task:
            forgot_response = client.post(
                "/api/v1/email/forgot-password",
                json={"email": sample_user_data["email"]}
            )
            assert forgot_response.status_code == status.HTTP_200_OK
            mock_task.assert_called_once()
        
        # 3. Сброс пароля
        with patch('app.utils.security.decode_verification_token') as mock_decode:
            mock_decode.return_value = {"sub": str(user.id), "email": user.email}
            
            reset_response = client.post(
                "/api/v1/email/reset-password",
                json={
                    "token": "mock_token",
                    "new_password": "new_secure_password123"
                }
            )
            assert reset_response.status_code == status.HTTP_200_OK
        
        # 4. Проверка что пароль изменился
        db_session.refresh(user)
        assert user.hashed_password != old_password_hash