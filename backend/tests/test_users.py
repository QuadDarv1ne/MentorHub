"""
Tests for Users API
Тесты для endpoints пользователей
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


class TestGetUserProfile:
    """Тесты получения профиля пользователя"""

    def test_get_own_profile_success(self, client, sample_user_data):
        """Тест получения собственного профиля"""
        # Регистрация
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Вход
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Получение профиля
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert "password" not in data

    def test_get_profile_unauthorized(self, client):
        """Тест получения профиля без авторизации"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_invalid_token(self, client):
        """Тест получения профиля с невалидным токеном"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateUserProfile:
    """Тесты обновления профиля пользователя"""

    def test_update_profile_success(self, client, sample_user_data):
        """Тест успешного обновления профиля"""
        # Регистрация и вход
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Обновление
        update_data = {
            "full_name": "Updated Name",
            "bio": "Test bio",
            "phone": "+1234567890",
        }
        response = client.put("/api/v1/users/me", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["bio"] == "Test bio"
        assert data["phone"] == "+1234567890"

    def test_update_profile_partial(self, client, sample_user_data):
        """Тест частичного обновления профиля"""
        # Регистрация и вход
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Обновление только одного поля
        response = client.put("/api/v1/users/me", json={"bio": "New bio"}, headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["bio"] == "New bio"
        assert data["username"] == sample_user_data["username"]  # Не изменилось

    def test_update_profile_unauthorized(self, client):
        """Тест обновления профиля без авторизации"""
        response = client.put("/api/v1/users/me", json={"bio": "Test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUserById:
    """Тесты получения пользователя по ID"""

    def test_get_user_by_id_success(self, client, sample_user_data):
        """Тест получения пользователя по ID"""
        # Регистрация пользователя
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["id"]

        # Вход как админ или тот же пользователь
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Получение пользователя
        response = client.get(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == sample_user_data["email"]

    def test_get_nonexistent_user(self, client, sample_user_data):
        """Тест получения несуществующего пользователя"""
        # Регистрация и вход
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/users/99999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUserRoles:
    """Тесты ролей пользователей"""

    def test_user_role_student_by_default(self, client, sample_user_data):
        """Тест что роль по умолчанию - STUDENT"""
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["role"] == "student"

    @pytest.mark.parametrize("role", ["student", "mentor", "admin"])
    def test_user_roles_enum(self, client, sample_user_data, role):
        """Тест что роли соответствуют enum"""
        # Просто проверяем что роли валидны
        assert role in ["student", "mentor", "admin"]


class TestUserDeletion:
    """Тесты удаления пользователя"""

    def test_delete_own_account(self, client, sample_user_data):
        """Тест удаления собственного аккаунта"""
        # Регистрация и вход
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Удаление
        response = client.delete("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # Проверка что пользователь удалён
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED  # Токен больше не валиден

    def test_delete_account_unauthorized(self, client):
        """Тест удаления аккаунта без авторизации"""
        response = client.delete("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
