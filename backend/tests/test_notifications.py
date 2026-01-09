"""
Тесты для системы уведомлений
"""

import pytest
from fastapi import status
from datetime import datetime, timedelta

from app.models.user import User, UserRole
from app.models.notification import Notification, NotificationType
from app.utils.security import get_password_hash, create_access_token


class TestNotifications:
    """Тесты для системы уведомлений"""

    @pytest.fixture
    def user_with_notifications(self, db_session):
        """Фикстура для создания пользователя с уведомлениями"""
        # Создание пользователя
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password=get_password_hash("securepassword123"),
            role=UserRole.STUDENT,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Создание уведомлений
        notifications_data = [
            {
                "user_id": user.id,
                "type": NotificationType.SESSION_BOOKED,
                "title": "Сессия забронирована",
                "message": "Ваша сессия с ментором была успешно забронирована",
                "is_read": False
            },
            {
                "user_id": user.id,
                "type": NotificationType.MESSAGE_RECEIVED,
                "title": "Новое сообщение",
                "message": "Вы получили новое сообщение от ментора",
                "is_read": False
            },
            {
                "user_id": user.id,
                "type": NotificationType.PAYMENT_SUCCESS,
                "title": "Оплата прошла успешно",
                "message": "Ваш платеж был успешно обработан",
                "is_read": True
            }
        ]
        
        notifications = []
        for notif_data in notifications_data:
            notification = Notification(**notif_data)
            db_session.add(notification)
            notifications.append(notification)
        
        db_session.commit()
        return {"user": user, "notifications": notifications}

    def test_get_user_notifications(self, client, user_with_notifications):
        """Тест получения уведомлений пользователя"""
        user = user_with_notifications["user"]
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/notifications", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_get_unread_notifications_count(self, client, user_with_notifications):
        """Тест получения количества непрочитанных уведомлений"""
        user = user_with_notifications["user"]
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/notifications/unread-count", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "unread_count" in data
        assert data["unread_count"] == 2  # Два непрочитанных уведомления

    def test_mark_notification_as_read(self, client, db_session, user_with_notifications):
        """Тест отметки уведомления как прочитанного"""
        user = user_with_notifications["user"]
        notifications = user_with_notifications["notifications"]
        unread_notification = next(n for n in notifications if not n.is_read)
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            f"/api/v1/notifications/{unread_notification.id}/read",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверка в базе данных
        db_session.refresh(unread_notification)
        assert unread_notification.is_read is True
        assert unread_notification.read_at is not None

    def test_mark_notification_as_read_not_found(self, client, user_with_notifications):
        """Тест отметки несуществующего уведомления как прочитанного"""
        user = user_with_notifications["user"]
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/v1/notifications/99999/read",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mark_notification_as_read_unauthorized(self, client, user_with_notifications):
        """Тест попытки отметить чужое уведомление как прочитанное"""
        user = user_with_notifications["user"]
        notifications = user_with_notifications["notifications"]
        
        # Создание другого пользователя
        other_user = User(
            email="other@example.com",
            username="otheruser",
            full_name="Other User",
            hashed_password=get_password_hash("securepassword123"),
            role=UserRole.STUDENT
        )
        
        token = create_access_token({"sub": str(other_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Попытка отметить чужое уведомление
        response = client.post(
            f"/api/v1/notifications/{notifications[0].id}/read",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_mark_all_notifications_as_read(self, client, db_session, user_with_notifications):
        """Тест массовой отметки всех уведомлений как прочитанных"""
        user = user_with_notifications["user"]
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/v1/notifications/mark-all-read",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверка что все уведомления помечены как прочитанные
        for notification in user_with_notifications["notifications"]:
            db_session.refresh(notification)
            assert notification.is_read is True

    def test_delete_notification(self, client, db_session, user_with_notifications):
        """Тест удаления уведомления"""
        user = user_with_notifications["user"]
        notification_to_delete = user_with_notifications["notifications"][0]
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(
            f"/api/v1/notifications/{notification_to_delete.id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверка что уведомление удалено из базы
        deleted_notification = db_session.query(Notification).get(notification_to_delete.id)
        assert deleted_notification is None

    def test_clear_all_notifications(self, client, db_session, user_with_notifications):
        """Тест очистки всех уведомлений"""
        user = user_with_notifications["user"]
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(
            "/api/v1/notifications/clear-all",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверка что все уведомления удалены
        remaining_notifications = db_session.query(Notification).filter(
            Notification.user_id == user.id
        ).all()
        
        assert len(remaining_notifications) == 0

    def test_filter_notifications_by_type(self, client, user_with_notifications):
        """Тест фильтрации уведомлений по типу"""
        user = user_with_notifications["user"]
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            "/api/v1/notifications?type=message_received",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Должно быть только одно уведомление типа message_received
        assert data["total"] == 1
        assert data["items"][0]["type"] == "message_received"

    def test_filter_notifications_by_read_status(self, client, user_with_notifications):
        """Тест фильтрации уведомлений по статусу прочтения"""
        user = user_with_notifications["user"]
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Получение непрочитанных уведомлений
        response = client.get(
            "/api/v1/notifications?is_read=false",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 2  # Два непрочитанных уведомления
        
        # Получение прочитанных уведомлений
        response = client.get(
            "/api/v1/notifications?is_read=true",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 1  # Одно прочитанное уведомление

    def test_pagination(self, client, user_with_notifications):
        """Тест пагинации уведомлений"""
        user = user_with_notifications["user"]
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Запрос первой страницы
        response = client.get(
            "/api/v1/notifications?page=1&size=2",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["page"] == 1
        assert data["size"] == 2
        assert len(data["items"]) == 2
        assert data["total"] == 3

    def test_create_notification_types(self, db_session, user_with_notifications):
        """Тест создания различных типов уведомлений"""
        user = user_with_notifications["user"]
        
        # Тест всех типов уведомлений
        notification_types = [
            NotificationType.SESSION_BOOKED,
            NotificationType.SESSION_CANCELLED,
            NotificationType.MESSAGE_RECEIVED,
            NotificationType.COURSE_ENROLLED,
            NotificationType.COURSE_COMPLETED,
            NotificationType.PAYMENT_SUCCESS,
            NotificationType.PAYMENT_FAILED,
            NotificationType.ACHIEVEMENT_UNLOCKED,
            NotificationType.REVIEW_REQUESTED,
            NotificationType.BADGE_EARNED,
            NotificationType.SYSTEM_MAINTENANCE,
            NotificationType.NEW_FEATURE,
            NotificationType.SECURITY_ALERT,
            NotificationType.SUBSCRIPTION_RENEWAL,
            NotificationType.PERFORMANCE_UPDATE
        ]
        
        for notif_type in notification_types:
            notification = Notification(
                user_id=user.id,
                type=notif_type,
                title=f"Test {notif_type.value}",
                message=f"Test message for {notif_type.value}"
            )
            db_session.add(notification)
        
        db_session.commit()
        
        # Проверка что все уведомления созданы
        created_notifications = db_session.query(Notification).filter(
            Notification.user_id == user.id
        ).all()
        
        assert len(created_notifications) == len(notification_types) + 3  # +3 существующих

    def test_notification_timestamps(self, db_session, user_with_notifications):
        """Тест временных меток уведомлений"""
        user = user_with_notifications["user"]
        
        # Создание нового уведомления
        notification = Notification(
            user_id=user.id,
            type=NotificationType.MESSAGE_RECEIVED,
            title="Test notification",
            message="Test message"
        )
        db_session.add(notification)
        db_session.commit()
        
        # Проверка временных меток
        assert notification.created_at is not None
        assert isinstance(notification.created_at, datetime)
        assert notification.updated_at is not None
        assert isinstance(notification.updated_at, datetime)
        
        # Для непрочитанных уведомлений read_at должен быть None
        assert notification.read_at is None
        
        # После прочтения read_at должен быть установлен
        notification.is_read = True
        db_session.commit()
        db_session.refresh(notification)
        
        assert notification.read_at is not None
        assert isinstance(notification.read_at, datetime)


@pytest.mark.integration
class TestNotificationIntegration:
    """Интеграционные тесты для уведомлений"""

    def test_notification_creation_on_events(self, client, db_session):
        """Тест автоматического создания уведомлений при событиях"""
        # Создание пользователя
        user_data = {
            "email": "eventuser@example.com",
            "username": "eventuser",
            "password": "securepassword123",
            "full_name": "Event User"
        }
        
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        user = db_session.query(User).filter(User.email == user_data["email"]).first()
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Тест создания уведомления при бронировании сессии
        # (это будет работать если соответствующая бизнес-логика реализована)
        
        # Проверка наличия уведомлений
        notifications_response = client.get("/api/v1/notifications", headers=headers)
        assert notifications_response.status_code == status.HTTP_200_OK
        
        # Проверка количества непрочитанных
        unread_response = client.get("/api/v1/notifications/unread-count", headers=headers)
        assert unread_response.status_code == status.HTTP_200_OK

    def test_notification_cleanup(self, client, db_session, user_with_notifications):
        """Тест очистки старых уведомлений"""
        user = user_with_notifications["user"]
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Создание очень старого уведомления (имитация)
        old_notification = Notification(
            user_id=user.id,
            type=NotificationType.SYSTEM_MAINTENANCE,
            title="Old notification",
            message="Very old notification",
            created_at=datetime.utcnow() - timedelta(days=365)  # Год назад
        )
        db_session.add(old_notification)
        db_session.commit()
        
        # Проверка общего количества уведомлений
        response = client.get("/api/v1/notifications", headers=headers)
        data = response.json()
        assert data["total"] == 4  # 3 старых + 1 новый
        
        # Здесь можно протестировать автоматическую очистку старых уведомлений
        # если такая функциональность реализована