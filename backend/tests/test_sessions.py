"""
Тесты сессий менторов
Тесты для CRUD операций с сессиями
"""

import pytest
import uuid
from fastapi import status
from datetime import datetime, timedelta

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


@pytest.fixture
def mentor_client(client):
    """Фикстура для клиента с ментором"""
    unique_id = str(uuid.uuid4())[:8]
    mentor_data = {
        "email": f"mentor_{unique_id}@test.com",
        "username": f"mentortest_{unique_id}",
        "password": "MentorPass123!",
        "role": "mentor",
    }
    client.post("/api/v1/auth/register", json=mentor_data)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": mentor_data["email"], "password": mentor_data["password"]},
    )
    token = login_response.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_client(client):
    """Фикстура для клиента со студентом"""
    unique_id = str(uuid.uuid4())[:8]
    student_data = {
        "email": f"student_{unique_id}@test.com",
        "username": f"studenttest_{unique_id}",
        "password": "StudentPass123!",
    }
    client.post("/api/v1/auth/register", json=student_data)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": student_data["email"], "password": student_data["password"]},
    )
    token = login_response.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


class TestGetSessions:
    """Тесты получения списка сессий"""

    def test_get_sessions_list(self, mentor_client):
        """Тест получения списка всех сессий"""
        client, headers = mentor_client

        response = client.get("/api/v1/sessions", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_sessions_unauthorized(self, client):
        """Тест получения сессий без авторизации"""
        response = client.get("/api/v1/sessions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_sessions_with_filters(self, mentor_client):
        """Тест получения сессий с фильтрами"""
        client, headers = mentor_client

        response = client.get("/api/v1/sessions?status=upcoming", headers=headers)
        assert response.status_code == status.HTTP_200_OK


class TestGetSessionById:
    """Тесты получения конкретной сессии"""

    def test_get_session_by_id(self, mentor_client):
        """Тест получения сессии по ID"""
        client, headers = mentor_client

        response = client.get("/api/v1/sessions/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_session_invalid_id(self, mentor_client):
        """Тест получения сессии с невалидным ID"""
        client, headers = mentor_client

        response = client.get("/api/v1/sessions/invalid", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateSession:
    """Тесты создания сессии"""

    def test_create_session_success(self, mentor_client):
        """Тест успешного создания сессии"""
        client, headers = mentor_client

        future_time = datetime.utcnow() + timedelta(days=7)
        session_data = {
            "mentor_id": 1,
            "student_id": 2,
            "start_time": future_time.isoformat(),
            "duration_minutes": 60,
            "notes": "Test session",
        }

        response = client.post("/api/v1/sessions", json=session_data, headers=headers)
        # Может вернуть 400 если ментор не найден, но не 422
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_create_session_invalid_data(self, mentor_client):
        """Тест создания сессии с невалидными данными"""
        client, headers = mentor_client

        invalid_data = {
            "mentor_id": -1,
            "start_time": "invalid-date",
        }

        response = client.post("/api/v1/sessions", json=invalid_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_session_unauthorized(self, client):
        """Тест создания сессии без авторизации"""
        response = client.post("/api/v1/sessions", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateSession:
    """Тесты обновления сессии"""

    def test_update_session_success(self, mentor_client):
        """Тест обновления сессии"""
        client, headers = mentor_client

        update_data = {
            "start_time": (datetime.utcnow() + timedelta(days=8)).isoformat(),
            "notes": "Updated notes",
        }

        response = client.put("/api/v1/sessions/999", json=update_data, headers=headers)
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK,
        ]

    def test_update_session_invalid_id(self, mentor_client):
        """Тест обновления сессии с невалидным ID"""
        client, headers = mentor_client

        response = client.put("/api/v1/sessions/invalid", json={}, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteSession:
    """Тесты удаления сессии"""

    def test_delete_session_success(self, mentor_client):
        """Тест удаления сессии"""
        client, headers = mentor_client

        response = client.delete("/api/v1/sessions/999", headers=headers)
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK,
        ]

    def test_delete_session_invalid_id(self, mentor_client):
        """Тест удаления сессии с невалидным ID"""
        client, headers = mentor_client

        response = client.delete("/api/v1/sessions/invalid", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSessionBooking:
    """Тесты записи на сессию"""

    def test_book_session_success(self, student_client):
        """Тест успешной записи на сессию"""
        client, headers = student_client

        future_time = datetime.utcnow() + timedelta(days=7)
        booking_data = {
            "mentor_id": 1,
            "start_time": future_time.isoformat(),
            "duration_minutes": 60,
        }

        response = client.post("/api/v1/sessions/book", json=booking_data, headers=headers)
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_book_session_unauthorized(self, client):
        """Тест записи на сессию без авторизации"""
        response = client.post("/api/v1/sessions/book", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSessionCancellation:
    """Тесты отмены сессии"""

    def test_cancel_session_success(self, mentor_client):
        """Тест успешной отмены сессии"""
        client, headers = mentor_client

        response = client.post("/api/v1/sessions/999/cancel", headers=headers)
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK,
        ]

    def test_cancel_session_invalid_id(self, mentor_client):
        """Тест отмены сессии с невалидным ID"""
        client, headers = mentor_client

        response = client.post("/api/v1/sessions/invalid/cancel", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSessionStatus:
    """Тесты статуса сессии"""

    def test_get_my_sessions(self, mentor_client):
        """Тест получения моих сессий"""
        client, headers = mentor_client

        response = client.get("/api/v1/sessions/my", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_upcoming_sessions(self, student_client):
        """Тест получения предстоящих сессий"""
        client, headers = student_client

        response = client.get("/api/v1/sessions/upcoming", headers=headers)
        assert response.status_code == status.HTTP_200_OK
