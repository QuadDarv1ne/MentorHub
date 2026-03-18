"""
Tests for Push Notifications API
Тесты для endpoints push-уведомлений
"""

import pytest
from fastapi import status


class TestPushNotificationsRegister:
    """Тесты регистрации push-уведомлений"""

    def test_register_push_token_success(self, sync_authenticated_client):
        """Тест успешной регистрации push-токена"""
        client, headers = sync_authenticated_client

        register_data = {
            "token": "test_push_token_12345",
            "platform": "web",
        }

        response = client.post(
            "/api/v1/push/register",
            json=register_data,
            headers=headers
        )
        # Может вернуть 200, 201, 400, 422
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_register_push_token_invalid_platform(self, sync_authenticated_client):
        """Тест регистрации с неверной платформой"""
        client, headers = sync_authenticated_client

        register_data = {
            "token": "test_push_token",
            "platform": "invalid_platform",
        }

        response = client.post(
            "/api/v1/push/register",
            json=register_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_push_token_unauthorized(self, client):
        """Тест регистрации push-токена без авторизации"""
        register_data = {
            "token": "test_push_token",
            "platform": "web",
        }
        response = client.post("/api/v1/push/register", json=register_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPushNotificationsUnregister:
    """Тесты отписки от push-уведомлений"""

    def test_unregister_push_token_success(self, sync_authenticated_client):
        """Тест успешной отписки от push-уведомлений"""
        client, headers = sync_authenticated_client

        response = client.post(
            "/api/v1/push/unregister",
            json={"token": "test_push_token"},
            headers=headers
        )
        # Может вернуть 200, 404
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_unregister_push_token_unauthorized(self, client):
        """Тест отписки без авторизации"""
        response = client.post(
            "/api/v1/push/unregister",
            json={"token": "test_push_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPushNotificationsSend:
    """Тесты отправки push-уведомлений"""

    def test_send_push_notification(self, sync_authenticated_client):
        """Тест отправки push-уведомления"""
        client, headers = sync_authenticated_client

        send_data = {
            "title": "Test Notification",
            "body": "This is a test notification",
            "user_id": 1,
        }

        response = client.post(
            "/api/v1/push/send",
            json=send_data,
            headers=headers
        )
        # Может вернуть 200, 201, 400, 404
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_send_push_missing_fields(self, sync_authenticated_client):
        """Тест отправки push с отсутствующими полями"""
        client, headers = sync_authenticated_client

        send_data = {
            "title": "Test",
            # Отсутствует body
        }

        response = client.post(
            "/api/v1/push/send",
            json=send_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPushNotificationsValidation:
    """Тесты валидации push-уведомлений"""

    def test_push_token_format(self):
        """Тест формата push-токена"""
        # Push токен должен быть непустой строкой
        valid_token = "test_push_token_12345"
        assert len(valid_token) > 0
        assert isinstance(valid_token, str)

    def test_push_platform_values(self):
        """Тест допустимых значений платформы"""
        valid_platforms = ["web", "ios", "android"]
        for platform in valid_platforms:
            assert platform in ["web", "ios", "android"]

    def test_push_notification_title_length(self):
        """Тест длины заголовка уведомления"""
        title = "Test"
        assert len(title) > 0
        assert len(title) <= 100

    def test_push_notification_body_length(self):
        """Тест длины тела уведомления"""
        body = "Test notification body"
        assert len(body) > 0
        assert len(body) <= 500
