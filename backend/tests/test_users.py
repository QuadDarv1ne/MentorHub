"""
Тесты пользователей
Расширенные тесты для CRUD операций с пользователями
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


class TestUserRead:
    """Тесты чтения пользователей"""

    def test_get_current_user(self, client, authenticated_headers):
        """Тест получения текущего пользователя"""
        # Регистрация и вход уже выполнены в authenticated_headers
        response = client.get("/api/v1/users/me", headers=authenticated_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert "username" in data
        assert "password" not in data

    def test_get_current_user_unauthorized(self, client):
        """Тест получения текущего пользователя без авторизации"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_by_id(self, client, create_user, authenticated_headers):
        """Тест получения пользователя по ID"""
        # Создаём тестового пользователя
        new_user = create_user(
            email="user2@example.com",
            username="user2",
            password="Password123!",
        )

        response = client.get(f"/api/v1/users/{new_user.id}", headers=authenticated_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == new_user.id
        assert data["email"] == new_user.email


class TestUserUpdate:
    """Тесты обновления пользователей"""

    def test_update_current_user(self, client, authenticated_headers):
        """Тест обновления текущего пользователя"""
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio",
        }

        response = client.put("/api/v1/users/me", json=update_data, headers=authenticated_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["bio"] == update_data["bio"]

    def test_update_user_email(self, client, authenticated_headers):
        """Тест обновления email пользователя"""
        update_data = {"email": "newemail@example.com"}

        response = client.put("/api/v1/users/me", json=update_data, headers=authenticated_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == update_data["email"]


class TestUserDelete:
    """Тесты удаления пользователей"""

    def test_delete_current_user(self, client):
        """Тест удаления текущего пользователя"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"test_{unique_id}@test.com",
            "username": f"testuser_{unique_id}",
            "password": "SecurePass123!",
        }
        
        # Регистрация
        client.post("/api/v1/auth/register", json=user_data)

        # Вход
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Удаление
        response = client.delete("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK

        # Проверка что пользователь удалён
        get_response = client.get("/api/v1/users/me", headers=headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestUserList:
    """Тесты списка пользователей"""

    def test_list_users(self, client, create_user, authenticated_headers):
        """Тест получения списка пользователей"""
        # Создаём несколько пользователей
        create_user(email="user1@example.com", username="user1", password="Password123!")
        create_user(email="user2@example.com", username="user2", password="Password123!")

        response = client.get("/api/v1/users", headers=authenticated_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data or isinstance(data, list)


class TestUserRoles:
    """Тесты ролей пользователей"""

    def test_create_admin_user(self, client):
        """Тест создания пользователя с ролью админа"""
        admin_data = {
            "email": "admin@example.com",
            "username": "adminuser",
            "password": "AdminPass123!",
            "role": "admin",
        }

        response = client.post("/api/v1/auth/register", json=admin_data)

        # Регистрация должна быть успешной
        assert response.status_code == status.HTTP_201_CREATED

    def test_mentor_profile_access(self, client, create_user):
        """Тест доступа к профилю ментора"""
        # Создаём ментора
        mentor = create_user(
            email="mentor@example.com",
            username="mentoruser",
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

        # Получение профиля
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "mentor"
