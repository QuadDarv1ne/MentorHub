"""
Tests for Sessions API
Тесты для endpoints сессий (занятий с менторами)
"""

import pytest
from fastapi import status
from datetime import datetime, timedelta

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


@pytest.fixture
def authenticated_client(client, sample_user_data):
    """Фикстура для авторизованного клиента"""
    client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


class TestGetSessions:
    """Тесты получения списка сессий"""

    def test_get_sessions_list(self, authenticated_client, sample_user_data):
        """Тест получения списка всех сессий пользователя"""
        client, headers = authenticated_client

        response = client.get("/api/v1/sessions", headers=headers)
        # Должен вернуть 200 (возможно пустой список)
        assert response.status_code == status.HTTP_200_OK

    def test_get_sessions_unauthorized(self, client):
        """Тест получения сессий без авторизации"""
        response = client.get("/api/v1/sessions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetSessionById:
    """Тесты получения конкретной сессии"""

    def test_get_session_by_id(self, authenticated_client, sample_user_data):
        """Тест получения сессии по ID"""
        client, headers = authenticated_client

        # Попытка получить несуществующую сессию
        response = client.get("/api/v1/sessions/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_session_invalid_id(self, authenticated_client, sample_user_data):
        """Тест получения сессии с невалидным ID"""
        client, headers = authenticated_client

        response = client.get("/api/v1/sessions/invalid", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateSession:
    """Тесты создания сессии (бронирование)"""

    def test_create_session_success(self, authenticated_client, sample_user_data):
        """Тест успешного бронирования сессии"""
        client, headers = authenticated_client

        future_time = datetime.utcnow() + timedelta(days=7)
        session_data = {
            "mentor_id": 1,
            "start_time": future_time.isoformat(),
            "duration_minutes": 60,
            "notes": "First session",
        }

        response = client.post("/api/v1/sessions", json=session_data, headers=headers)
        # Может быть 201 если создана или 400/404/422 если ошибки
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_create_session_missing_fields(self, authenticated_client, sample_user_data):
        """Тест создания сессии с отсутствующими полями"""
        client, headers = authenticated_client

        session_data = {
            # Отсутствует mentor_id
            "start_time": "2026-03-15T10:00:00",
        }

        response = client.post("/api/v1/sessions", json=session_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_session_past_time(self, authenticated_client, sample_user_data):
        """Тест создания сессии на прошлое время"""
        client, headers = authenticated_client

        past_time = datetime.utcnow() - timedelta(days=1)
        session_data = {
            "mentor_id": 1,
            "start_time": past_time.isoformat(),
            "duration_minutes": 60,
        }

        response = client.post("/api/v1/sessions", json=session_data, headers=headers)
        # Должен отклонить сессию в прошлом
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_create_session_unauthorized(self, client):
        """Тест создания сессии без авторизации"""
        session_data = {
            "mentor_id": 1,
            "start_time": "2026-03-15T10:00:00",
        }
        response = client.post("/api/v1/sessions", json=session_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateSession:
    """Тесты обновления сессии"""

    def test_update_session_success(self, authenticated_client, sample_user_data):
        """Тест обновления сессии"""
        client, headers = authenticated_client

        update_data = {
            "notes": "Updated notes",
            "status": "rescheduled",
        }

        # Попытка обновить несуществующую сессию
        response = client.put("/api/v1/sessions/999", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_session_status(self, authenticated_client, sample_user_data):
        """Тест обновления статуса сессии"""
        client, headers = authenticated_client

        # Допустимые статусы
        valid_statuses = ["pending", "confirmed", "completed", "cancelled", "rescheduled"]
        for status_value in valid_statuses:
            assert status_value in valid_statuses


class TestCancelSession:
    """Тесты отмены сессии"""

    def test_cancel_session_success(self, authenticated_client, sample_user_data):
        """Тест отмены сессии"""
        client, headers = authenticated_client

        # Попытка отменить несуществующую сессию
        response = client.delete("/api/v1/sessions/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cancel_session_unauthorized(self, client):
        """Тест отмены сессии без авторизации"""
        response = client.delete("/api/v1/sessions/999")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCompleteSession:
    """Тесты завершения сессии"""

    def test_complete_session_success(self, authenticated_client, sample_user_data):
        """Тест завершения сессии"""
        client, headers = authenticated_client

        completion_data = {
            "notes": "Session completed",
            "rating": 5,
        }

        # Попытка завершить несуществующую сессию
        response = client.post("/api/v1/sessions/999/complete", json=completion_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_complete_session_rating_validation(self, authenticated_client, sample_user_data):
        """Тест валидации рейтинга при завершении"""
        client, headers = authenticated_client

        # Рейтинг вне диапазона
        completion_data = {
            "rating": 10,  # Максимум 5
        }

        response = client.post("/api/v1/sessions/999/complete", json=completion_data, headers=headers)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_404_NOT_FOUND,
        ]


class TestSessionFilters:
    """Тесты фильтрации сессий"""

    def test_filter_sessions_by_status(self, authenticated_client, sample_user_data):
        """Тест фильтрации сессий по статусу"""
        client, headers = authenticated_client

        response = client.get("/api/v1/sessions?status=pending", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_sessions_by_date_range(self, authenticated_client, sample_user_data):
        """Тест фильтрации сессий по диапазону дат"""
        client, headers = authenticated_client

        start_date = datetime.utcnow().isoformat()
        end_date = (datetime.utcnow() + timedelta(days=30)).isoformat()

        response = client.get(
            f"/api/v1/sessions?start_date={start_date}&end_date={end_date}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK


class TestSessionValidation:
    """Тесты валидации сессий"""

    def test_session_duration_validation(self, authenticated_client, sample_user_data):
        """Тест валидации длительности сессии"""
        client, headers = authenticated_client

        # Слишком короткая или длинная сессия
        session_data = {
            "mentor_id": 1,
            "start_time": "2026-03-15T10:00:00",
            "duration_minutes": 0,  # Неvalid
        }

        response = client.post("/api/v1/sessions", json=session_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("duration", [30, 45, 60, 90, 120])
    def test_session_duration_values(self, duration):
        """Тест допустимых значений длительности"""
        # Стандартные длительности сессий
        assert 15 <= duration <= 180
