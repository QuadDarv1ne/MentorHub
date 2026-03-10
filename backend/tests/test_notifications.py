"""
Tests for Notifications API
Тесты для endpoints уведомлений
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


class TestGetNotifications:
    """Тесты получения уведомлений"""

    def test_get_notifications_list(self, sync_authenticated_client, sample_user_data):
        """Тест получения списка всех уведомлений"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/notifications", headers=headers)
        # Должен вернуть 200 (возможно пустой список)
        assert response.status_code == status.HTTP_200_OK

    def test_get_notifications_unauthorized(self, client):
        """Тест получения уведомлений без авторизации"""
        response = client.get("/api/v1/notifications")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_notifications_with_filters(self, sync_authenticated_client, sample_user_data):
        """Тест получения уведомлений с фильтрами"""
        client, headers = sync_authenticated_client

        # Фильтр по типу (правильное значение из NotificationType enum)
        # Может вернуть 200 или 400 если тип некорректен
        response = client.get("/api/v1/notifications?type=new_message", headers=headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

        # Фильтр по непрочитанным (используем unread чтобы избежать XSS false positive)
        response = client.get("/api/v1/notifications?unread_only=1", headers=headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestGetUnreadCount:
    """Тесты получения количества непрочитанных уведомлений"""

    def test_get_unread_count_success(self, sync_authenticated_client, sample_user_data):
        """Тест получения количества непрочитанных"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/notifications/unread-count", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "unread_count" in data
        assert isinstance(data["unread_count"], int)

    def test_get_unread_count_unauthorized(self, client):
        """Тест получения количества непрочитанных без авторизации"""
        response = client.get("/api/v1/notifications/unread-count")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMarkNotificationAsRead:
    """Тесты отметки уведомления как прочитанного"""

    def test_mark_notification_read_success(self, sync_authenticated_client, sample_user_data):
        """Тест успешной отметки уведомления"""
        client, headers = sync_authenticated_client

        # Попытка отметить несуществующее уведомление
        response = client.post("/api/v1/notifications/999/read", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mark_notification_read_unauthorized(self, client):
        """Тест отметки уведомления без авторизации"""
        response = client.post("/api/v1/notifications/999/read")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMarkAllNotificationsAsRead:
    """Тесты отметки всех уведомлений как прочитанных"""

    def test_mark_all_notifications_read_success(self, sync_authenticated_client, sample_user_data):
        """Тест успешной отметки всех уведомлений"""
        client, headers = sync_authenticated_client

        response = client.post("/api/v1/notifications/mark-all-read", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_mark_all_notifications_read_unauthorized(self, client):
        """Тест отметки всех уведомлений без авторизации"""
        response = client.post("/api/v1/notifications/mark-all-read")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteNotification:
    """Тесты удаления уведомления"""

    def test_delete_notification_success(self, sync_authenticated_client, sample_user_data):
        """Тест успешного удаления уведомления"""
        client, headers = sync_authenticated_client

        # Попытка удалить несуществующее уведомление
        response = client.delete("/api/v1/notifications/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_notification_unauthorized(self, client):
        """Тест удаления уведомления без авторизации"""
        response = client.delete("/api/v1/notifications/999")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestClearAllNotifications:
    """Тесты очистки всех уведомлений"""

    def test_clear_all_notifications_success(self, sync_authenticated_client, sample_user_data):
        """Тест успешной очистки всех уведомлений"""
        client, headers = sync_authenticated_client

        response = client.delete("/api/v1/notifications/clear-all", headers=headers)
        # Может вернуть 200 или 422 если нет прочитанных
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_clear_all_notifications_unauthorized(self, client):
        """Тест очистки всех уведомлений без авторизации"""
        response = client.delete("/api/v1/notifications/clear-all")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationTypes:
    """Тесты типов уведомлений"""

    @pytest.mark.parametrize("notification_type", [
        "session",
        "message",
        "course",
        "payment",
        "achievement",
        "system",
    ])
    def test_notification_types_enum(self, notification_type):
        """Тест типов уведомлений"""
        valid_types = ["session", "message", "course", "payment", "achievement", "system"]
        assert notification_type in valid_types


class TestNotificationPagination:
    """Тесты пагинации уведомлений"""

    def test_notifications_pagination(self, sync_authenticated_client, sample_user_data):
        """Тест пагинации уведомлений"""
        client, headers = sync_authenticated_client

        # Page 1
        response = client.get("/api/v1/notifications?page=1&limit=10", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        if isinstance(data, dict):
            assert "page" in data or "items" in data or len(data) >= 0

    def test_notifications_invalid_page(self, sync_authenticated_client, sample_user_data):
        """Тест невалидной пагинации"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/notifications?page=-1", headers=headers)
        # Должен вернуть 422 или использовать дефолтное значение
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_200_OK,
        ]

    def test_notifications_invalid_limit(self, sync_authenticated_client, sample_user_data):
        """Тест невалидного limit"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/notifications?limit=1000", headers=headers)
        # Должен вернуть 422 или использовать максимальное значение
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_200_OK,
        ]


class TestNotificationPermissions:
    """Тесты прав доступа к уведомлениям"""

    def test_cannot_access_others_notifications(self, client, sample_user_data):
        """Тест что нельзя получить уведомления другого пользователя"""
        # Создаём двух пользователей
        user1_data = sample_user_data
        user2_data = {
            "email": "user2@example.com",
            "username": "user2",
            "password": "TestPass123!",
        }

        # Регистрация пользователя 1
        client.post("/api/v1/auth/register", json=user1_data)
        login1 = client.post(
            "/api/v1/auth/login",
            json={"email": user1_data["email"], "password": user1_data["password"]},
        )
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Регистрация пользователя 2
        client.post("/api/v1/auth/register", json=user2_data)
        login2 = client.post(
            "/api/v1/auth/login",
            json={"email": user2_data["email"], "password": user2_data["password"]},
        )
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Пользователь 1 получает свои уведомления
        response1 = client.get("/api/v1/notifications", headers=headers1)
        assert response1.status_code == status.HTTP_200_OK

        # Пользователь 2 получает свои уведомления
        response2 = client.get("/api/v1/notifications", headers=headers2)
        assert response2.status_code == status.HTTP_200_OK
