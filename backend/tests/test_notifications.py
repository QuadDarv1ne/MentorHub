"""
Tests for Notifications API
Тесты для endpoints уведомлений
"""

import pytest
from fastapi import status


class TestGetNotifications:
    """Тесты получения уведомлений"""

    def test_get_notifications_list(self, sync_authenticated_client):
        """Тест получения списка всех уведомлений"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/notifications", headers=headers)
        # Должен вернуть 200 (возможно пустой список)
        assert response.status_code == status.HTTP_200_OK

    def test_get_notifications_unauthorized(self, client):
        """Тест получения уведомлений без авторизации"""
        response = client.get("/api/v1/notifications")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUnreadCount:
    """Тесты получения количества непрочитанных уведомлений"""

    def test_get_unread_count_success(self, sync_authenticated_client):
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

    def test_mark_notification_read_not_found(self, sync_authenticated_client):
        """Тест отметки несуществующего уведомления"""
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

    def test_mark_all_notifications_read_success(self, sync_authenticated_client):
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

    def test_delete_notification_not_found(self, sync_authenticated_client):
        """Тест удаления несуществующего уведомления"""
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

    def test_clear_all_notifications_success(self, sync_authenticated_client):
        """Тест успешной очистки всех уведомлений"""
        client, headers = sync_authenticated_client

        response = client.delete("/api/v1/notifications/clear-all", headers=headers)
        # Может вернуть 200 или 422 если нет прочитанных
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_clear_all_notifications_unauthorized(self, client):
        """Тест очистки всех уведомлений без авторизации"""
        response = client.delete("/api/v1/notifications/clear-all")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationPagination:
    """Тесты пагинации уведомлений"""

    def test_notifications_pagination(self, sync_authenticated_client):
        """Тест пагинации уведомлений"""
        client, headers = sync_authenticated_client

        # Page 1
        response = client.get("/api/v1/notifications?page=1&limit=10", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_notifications_invalid_page(self, sync_authenticated_client):
        """Тест невалидной пагинации"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/notifications?page=-1", headers=headers)
        # Должен вернуть 422 или использовать дефолтное значение
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_200_OK,
        ]
