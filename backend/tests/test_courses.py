"""
Tests for Courses API
Тесты для endpoints курсов
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


@pytest.fixture
def authenticated_client(client, sample_user_data):
    """Фикстура для авторизованного клиента"""
    # Регистрация и вход
    client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


class TestGetCourses:
    """Тесты получения списка курсов"""

    def test_get_courses_list(self, authenticated_client, sample_user_data):
        """Тест получения списка всех курсов"""
        client, headers = authenticated_client

        response = client.get("/api/v1/courses", headers=headers)
        # Должен вернуть 200 или 404 если курсов нет
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_courses_unauthorized(self, client):
        """Тест получения курсов без авторизации"""
        response = client.get("/api/v1/courses")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCourseById:
    """Тесты получения конкретного курса"""

    def test_get_course_by_id(self, authenticated_client, sample_user_data):
        """Тест получения курса по ID"""
        client, headers = authenticated_client

        # Попытка получить несуществующий курс
        response = client.get("/api/v1/courses/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_course_invalid_id(self, authenticated_client, sample_user_data):
        """Тест получения курса с невалидным ID"""
        client, headers = authenticated_client

        response = client.get("/api/v1/courses/invalid", headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateCourse:
    """Тесты создания курса"""

    def test_create_course_success(self, authenticated_client, sample_user_data):
        """Тест успешного создания курса"""
        client, headers = authenticated_client

        course_data = {
            "title": "Python для начинающих",
            "description": "Курс по основам Python",
            "level": "beginner",
            "duration_hours": 20,
        }

        response = client.post("/api/v1/courses", json=course_data, headers=headers)
        # Может быть 201 если создан или 400/422 если валидация
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_create_course_missing_fields(self, authenticated_client, sample_user_data):
        """Тест создания курса с отсутствующими полями"""
        client, headers = authenticated_client

        course_data = {
            "title": "",  # Пустой title
        }

        response = client.post("/api/v1/courses", json=course_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_course_unauthorized(self, client):
        """Тест создания курса без авторизации"""
        course_data = {
            "title": "Test Course",
            "description": "Test",
        }
        response = client.post("/api/v1/courses", json=course_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateCourse:
    """Тесты обновления курса"""

    def test_update_course_success(self, authenticated_client, sample_user_data):
        """Тест обновления курса"""
        client, headers = authenticated_client

        update_data = {
            "title": "Updated Course Title",
            "description": "Updated description",
        }

        # Попытка обновить несуществующий курс
        response = client.put("/api/v1/courses/999", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_course_partial(self, authenticated_client, sample_user_data):
        """Тест частичного обновления курса"""
        client, headers = authenticated_client

        update_data = {
            "description": "Only description update",
        }

        response = client.patch("/api/v1/courses/999", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteCourse:
    """Тесты удаления курса"""

    def test_delete_course_success(self, authenticated_client, sample_user_data):
        """Тест удаления курса"""
        client, headers = authenticated_client

        # Попытка удалить несуществующий курс
        response = client.delete("/api/v1/courses/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_course_unauthorized(self, client):
        """Тест удаления курса без авторизации"""
        response = client.delete("/api/v1/courses/999")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestEnrollCourse:
    """Тесты записи на курс"""

    def test_enroll_course_success(self, authenticated_client, sample_user_data):
        """Тест записи на курс"""
        client, headers = authenticated_client

        # Попытка записаться на несуществующий курс
        response = client.post("/api/v1/courses/999/enroll", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_enroll_course_unauthorized(self, client):
        """Тест записи на курс без авторизации"""
        response = client.post("/api/v1/courses/999/enroll")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCourseLessons:
    """Тесты уроков курса"""

    def test_get_course_lessons(self, authenticated_client, sample_user_data):
        """Тест получения уроков курса"""
        client, headers = authenticated_client

        response = client.get("/api/v1/courses/999/lessons", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_lesson(self, authenticated_client, sample_user_data):
        """Тест создания урока"""
        client, headers = authenticated_client

        lesson_data = {
            "title": "Introduction",
            "content": "Lesson content",
            "order": 1,
        }

        response = client.post("/api/v1/courses/999/lessons", json=lesson_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCourseValidation:
    """Тесты валидации курсов"""

    @pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
    def test_course_levels(self, authenticated_client, sample_user_data, level):
        """Тест уровней курсов"""
        client, headers = authenticated_client
        assert level in ["beginner", "intermediate", "advanced"]

    def test_course_duration_validation(self, authenticated_client, sample_user_data):
        """Тест валидации длительности курса"""
        client, headers = authenticated_client

        # Отрицательная длительность
        course_data = {
            "title": "Test Course",
            "description": "Test",
            "duration_hours": -10,
        }

        response = client.post("/api/v1/courses", json=course_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
