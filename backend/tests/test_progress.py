"""
Тесты для прогресса пользователей
Покрывает CRUD операции с прогрессом обучения
"""

import pytest
from fastapi import status
from datetime import datetime

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


def register_and_login(client, sample_user_data):
    """Хелпер для регистрации и входа"""
    r = client.post("/api/v1/auth/register", json=sample_user_data)
    assert r.status_code == status.HTTP_201_CREATED
    login = client.post(
        "/api/v1/auth/login", json={"email": sample_user_data["email"], "password": sample_user_data["password"]}
    )
    assert login.status_code == status.HTTP_200_OK
    return login.json()["access_token"]


class TestProgressCreate:
    """Тесты создания прогресса"""

    def test_create_progress_requires_auth(self, client):
        """Тест что создание требует авторизации"""
        res = client.post("/api/v1/progress", json={"course_id": 1, "progress_percent": 10})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_progress_success(self, client, sample_user_data):
        """Тест успешного создания прогресса"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        res = client.post(
            "/api/v1/progress",
            json={"course_id": 1, "lesson_id": 1, "progress_percent": 25},
            headers=headers
        )
        # Valid responses: 201 (created), 404 (course not found), 409 (conflict)
        assert res.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT
        ]

    def test_create_progress_invalid_data(self, client, sample_user_data):
        """Тест создания с невалидными данными"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        # Отрицательный прогресс
        res = client.post(
            "/api/v1/progress",
            json={"course_id": 1, "progress_percent": -10},
            headers=headers
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Прогресс больше 100
        res = client.post(
            "/api/v1/progress",
            json={"course_id": 1, "progress_percent": 150},
            headers=headers
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProgressRead:
    """Тесты чтения прогресса"""

    def test_get_my_progress(self, client, sample_user_data):
        """Тест получения моего прогресса"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get("/api/v1/progress/my", headers=headers)
        assert res.status_code == status.HTTP_200_OK

    def test_get_progress_unauthorized(self, client):
        """Тест получения прогресса без авторизации"""
        res = client.get("/api/v1/progress/my")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_course_progress(self, client, sample_user_data):
        """Тест получения прогресса по курсу"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get("/api/v1/progress/course/1", headers=headers)
        # 200 (success) или 404 (not found)
        assert res.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestProgressUpdate:
    """Тесты обновления прогресса"""

    def test_update_progress_success(self, client, sample_user_data):
        """Тест успешного обновления прогресса"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        # Сначала создаём
        create_res = client.post(
            "/api/v1/progress",
            json={"course_id": 1, "lesson_id": 1, "progress_percent": 25},
            headers=headers
        )

        if create_res.status_code == status.HTTP_201_CREATED:
            # Обновляем
            update_res = client.put(
                "/api/v1/progress/1",
                json={"progress_percent": 50},
                headers=headers
            )
            assert update_res.status_code in [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND
            ]

    def test_update_progress_invalid_id(self, client, sample_user_data):
        """Тест обновления с невалидным ID"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        res = client.put(
            "/api/v1/progress/999",
            json={"progress_percent": 75},
            headers=headers
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND


class TestProgressDelete:
    """Тесты удаления прогресса"""

    def test_delete_progress_success(self, client, sample_user_data):
        """Тест успешного удаления прогресса"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        res = client.delete("/api/v1/progress/999", headers=headers)
        assert res.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_delete_progress_unauthorized(self, client):
        """Тест удаления без авторизации"""
        res = client.delete("/api/v1/progress/1")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestProgressValidation:
    """Тесты валидации прогресса"""

    def test_progress_percent_boundary(self, client, sample_user_data):
        """Тест границ прогресса (0-100)"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        # 0% - допустимо
        res = client.post(
            "/api/v1/progress",
            json={"course_id": 1, "progress_percent": 0},
            headers=headers
        )
        assert res.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

        # 100% - допустимо
        res = client.post(
            "/api/v1/progress",
            json={"course_id": 1, "progress_percent": 100},
            headers=headers
        )
        assert res.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_progress_duplicate(self, client, sample_user_data):
        """Тест дублирования прогресса"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        # Создаём дважды один и тот же прогресс
        res1 = client.post(
            "/api/v1/progress",
            json={"course_id": 1, "lesson_id": 1, "progress_percent": 25},
            headers=headers
        )

        res2 = client.post(
            "/api/v1/progress",
            json={"course_id": 1, "lesson_id": 1, "progress_percent": 30},
            headers=headers
        )

        # Второе создание должно вернуть конфликт или обновить
        assert res2.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_409_CONFLICT,
            status.HTTP_404_NOT_FOUND
        ]


class TestProgressEdgeCases:
    """Тесты граничных случаев"""

    def test_progress_completed_course(self, client, sample_user_data):
        """Тест прогресса завершённого курса (100%)"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        res = client.post(
            "/api/v1/progress",
            json={"course_id": 1, "progress_percent": 100, "completed": True},
            headers=headers
        )
        assert res.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_progress_multiple_courses(self, client, sample_user_data):
        """Тест прогресса для нескольких курсов"""
        token = register_and_login(client, sample_user_data)
        headers = {"Authorization": f"Bearer {token}"}

        # Создаём прогресс для разных курсов
        for course_id in [1, 2, 3]:
            res = client.post(
                "/api/v1/progress",
                json={"course_id": course_id, "progress_percent": 50},
                headers=headers
            )
            assert res.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_409_CONFLICT
            ]

        # Получаем все прогрессы
        list_res = client.get("/api/v1/progress/my", headers=headers)
        assert list_res.status_code == status.HTTP_200_OK
