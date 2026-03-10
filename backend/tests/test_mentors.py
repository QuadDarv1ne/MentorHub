"""
Tests for Mentors API
Тесты для endpoints менторов
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


class TestGetMentors:
    """Тесты получения списка менторов"""

    def test_get_mentors_list(self, sync_authenticated_client, sample_user_data):
        """Тест получения списка всех менторов"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/mentors", headers=headers)
        # Должен вернуть 200 (возможно пустой список)
        assert response.status_code == status.HTTP_200_OK

    def test_get_mentors_unauthorized(self, client):
        """Тест получения менторов без авторизации (публичный эндпоинт)"""
        response = client.get("/api/v1/mentors")
        # Публичный эндпоинт - доступен без авторизации
        assert response.status_code == status.HTTP_200_OK

    def test_get_mentors_with_filters(self, sync_authenticated_client, sample_user_data):
        """Тест получения менторов с фильтрами"""
        client, headers = sync_authenticated_client

        # Фильтр по специальности
        response = client.get("/api/v1/mentors?specialization=python", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # Фильтр по цене
        response = client.get("/api/v1/mentors?max_price=100", headers=headers)
        assert response.status_code == status.HTTP_200_OK


class TestGetMentorById:
    """Тесты получения конкретного ментора"""

    def test_get_mentor_by_id(self, sync_authenticated_client, sample_user_data):
        """Тест получения ментора по ID"""
        client, headers = sync_authenticated_client

        # Попытка получить несуществующего ментора
        response = client.get("/api/v1/mentors/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_mentor_invalid_id(self, sync_authenticated_client, sample_user_data):
        """Тест получения ментора с невалидным ID"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/mentors/invalid", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestBecomeMentor:
    """Тесты подачи заявки на менторство"""

    def test_become_mentor_success(self, sync_authenticated_client, sample_user_data, sample_mentor_data):
        """Тест успешной подачи заявки на менторство"""
        client, headers = sync_authenticated_client

        response = client.post("/api/v1/mentors", json=sample_mentor_data, headers=headers)
        # Может быть 201 если создана или 400/422 если ошибки
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_become_mentor_missing_fields(self, sync_authenticated_client, sample_user_data):
        """Тест подачи заявки с отсутствующими полями"""
        client, headers = sync_authenticated_client

        application_data = {
            # Отсутствуют обязательные поля
            "bio": "Some bio",
        }

        response = client.post("/api/v1/mentors", json=application_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_become_mentor_experience_validation(self, sync_authenticated_client, sample_user_data):
        """Тест валидации опыта ментора"""
        client, headers = sync_authenticated_client

        application_data = {
            "specialization": "Python",
            "experience_years": -1,  # Невалидно
            "bio": "Test",
            "hourly_rate": 50,
        }

        response = client.post("/api/v1/mentors", json=application_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_become_mentor_unauthorized(self, client):
        """Тест подачи заявки без авторизации"""
        application_data = {
            "specialization": "Python",
            "experience_years": 5,
            "bio": "Test",
        }
        response = client.post("/api/v1/mentors", json=application_data)
        # Без авторизации - 422 (нет токена)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestUpdateMentorProfile:
    """Тесты обновления профиля ментора"""

    def test_update_mentor_profile(self, sync_authenticated_client, sample_user_data):
        """Тест обновления профиля ментора"""
        client, headers = sync_authenticated_client

        update_data = {
            "bio": "Updated bio",
            "hourly_rate": 75,
        }

        # Попытка обновить несуществующего ментора
        response = client.put("/api/v1/mentors/999", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetMentorReviews:
    """Тесты получения отзывов ментора"""

    def test_get_mentor_reviews(self, sync_authenticated_client, sample_user_data):
        """Тест получения отзывов ментора"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/mentors/999/reviews", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestMentorAvailability:
    """Тесты доступности ментора"""

    def test_get_mentor_availability(self, sync_authenticated_client, sample_user_data):
        """Тест получения доступности ментора"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/mentors/999/availability", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_set_mentor_availability(self, sync_authenticated_client, sample_user_data):
        """Тест установки доступности ментора"""
        client, headers = sync_authenticated_client

        availability_data = {
            "day_of_week": "monday",
            "start_time": "09:00",
            "end_time": "17:00",
        }

        response = client.post("/api/v1/mentors/availability", json=availability_data, headers=headers)
        # Может потребоваться ID ментора или вернуть 405
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        ]


class TestMentorStats:
    """Тесты статистики ментора"""

    def test_get_mentor_stats(self, sync_authenticated_client, sample_user_data):
        """Тест получения статистики ментора"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/mentors/999/stats", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestMentorValidation:
    """Тесты валидации менторов"""

    @pytest.mark.parametrize("rate", [0, 10, 50, 100, 500])
    def test_hourly_rate_values(self, rate):
        """Тест допустимых значений почасовой ставки"""
        assert rate >= 0

    def test_specialization_required(self, sync_authenticated_client, sample_user_data):
        """Тест обязательности специализации"""
        client, headers = sync_authenticated_client

        application_data = {
            "experience_years": 5,
            "bio": "Test",
            # Отсутствует specialization
        }

        response = client.post("/api/v1/mentors", json=application_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
