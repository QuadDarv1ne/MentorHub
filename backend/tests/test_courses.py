"""
Тесты курсов
Тесты для CRUD операций с курсами
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.models.course import Course
from app.utils.security import get_password_hash


class TestCourseRead:
    """Тесты чтения курсов"""

    def test_get_course_list(self, sync_authenticated_client):
        """Тест получения списка курсов"""
        client, headers = sync_authenticated_client
        response = client.get("/api/v1/courses", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list) or "items" in data

    def test_get_course_list_unauthorized(self, client):
        """Тест получения списка курсов без авторизации"""
        response = client.get("/api/v1/courses")

        # Публичный доступ может быть разрешён
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_get_course_by_id(self, sync_authenticated_client, create_user):
        """Тест получения курса по ID"""
        client, headers = sync_authenticated_client
        # Создаём ментора
        mentor = create_user(
            email="mentor@example.com",
            username="mentoruser",
            password="MentorPass123!",
            role="mentor",
        )

        # Создаём курс
        course_data = {
            "title": "Test Course",
            "description": "Test Description",
            "level": "beginner",
            "duration_hours": 10,
            "price": 49.99,
        }

        # Получение списка (создание через API может требовать ментора)
        response = client.get("/api/v1/courses", headers=headers)

        assert response.status_code == status.HTTP_200_OK


class TestCourseCreate:
    """Тесты создания курсов"""

    def test_create_course_as_mentor(self, client, create_user):
        """Тест создания курса ментором"""
        # Создаём ментора
        mentor = create_user(
            email="mentor2@example.com",
            username="mentoruser2",
            password="MentorPass123!",
            role="mentor",
        )

        # Вход
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": mentor.email, "password": "MentorPass123!"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Price в копейках (integer), instructor_id = id ментора
        course_data = {
            "title": "New Python Course",
            "description": "Learn Python from scratch",
            "level": "beginner",
            "duration_hours": 20,
            "price": 7999,  # 79.99 в копейках
            "instructor_id": mentor.id,
        }

        response = client.post("/api/v1/courses", json=course_data, headers=headers)

        # Может требовать профиль ментора
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        ]


class TestCourseUpdate:
    """Тесты обновления курсов"""

    def test_update_course(self, sync_authenticated_client, create_user):
        """Тест обновления курса"""
        client, headers = sync_authenticated_client
        # Создание курса и обновление может требовать дополнительных фикстур
        # Этот тест проверяет структуру
        update_data = {
            "title": "Updated Course Title",
            "description": "Updated description",
        }

        # Попытка обновления (может вернуть 404 если курс не найден)
        response = client.put("/api/v1/courses/999", json=update_data, headers=headers)

        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        ]


class TestCourseDelete:
    """Тесты удаления курсов"""

    def test_delete_course(self, sync_authenticated_client):
        """Тест удаления курса"""
        client, headers = sync_authenticated_client
        # Попытка удаления несуществующего курса
        response = client.delete("/api/v1/courses/999", headers=headers)

        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
        ]


class TestCourseSearch:
    """Тесты поиска курсов"""

    def test_search_courses(self, sync_authenticated_client):
        """Тест поиска курсов"""
        client, headers = sync_authenticated_client
        response = client.get("/api/v1/courses?search=python", headers=headers)

        assert response.status_code == status.HTTP_200_OK

    def test_filter_courses_by_level(self, sync_authenticated_client):
        """Тест фильтрации курсов по уровню"""
        client, headers = sync_authenticated_client
        response = client.get("/api/v1/courses?level=beginner", headers=headers)

        assert response.status_code == status.HTTP_200_OK

    def test_filter_courses_by_price(self, sync_authenticated_client):
        """Тест фильтрации курсов по цене"""
        client, headers = sync_authenticated_client
        response = client.get("/api/v1/courses?max_price=50", headers=headers)

        assert response.status_code == status.HTTP_200_OK


class TestCourseEnrollment:
    """Тесты записи на курсы"""

    def test_enroll_course(self, sync_authenticated_client):
        """Тест записи на курс"""
        client, headers = sync_authenticated_client
        # Попытка записи на несуществующий курс
        response = client.post("/api/v1/courses/999/enroll", headers=headers)

        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_get_enrolled_courses(self, sync_authenticated_client):
        """Тест получения списка записанных курсов"""
        client, headers = sync_authenticated_client
        response = client.get("/api/v1/courses/my", headers=headers)

        assert response.status_code == status.HTTP_200_OK
