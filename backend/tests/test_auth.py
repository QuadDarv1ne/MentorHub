"""
Тесты аутентификации
Тесты для эндпоинтов аутентификации
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


class TestRegistration:
    """Тесты регистрации пользователей"""

    def test_register_success(self, client, sample_user_data):
        """Тест успешной регистрации пользователя"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert "password" not in data

    def test_register_duplicate_email(self, client, db_session, sample_user_data):
        """Тест регистрации с дублирующимся email"""
        # Создание существующего пользователя
        existing_user = User(
            email=sample_user_data["email"],
            username="existinguser",
            hashed_password=get_password_hash(sample_user_data["password"]),
            role=UserRole.STUDENT,
        )
        db_session.add(existing_user)
        db_session.commit()

        # Попытка регистрации с тем же email
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_data(self, client):
        """Тест регистрации с невалидными данными"""
        invalid_data = {
            "email": "not-an-email",
            "username": "ab",  # Слишком короткий
            "password": "123",  # Слишком короткий
        }

        response = client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Тесты входа пользователей"""

    def test_login_success(self, client, db_session, sample_user_data):
        """Тест успешного входа"""
        # Сначала регистрация пользователя
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Вход
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, sample_user_data):
        """Тест входа с неверными учетными данными"""
        login_data = {
            "email": sample_user_data["email"],
            "password": "wrongpassword",
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword",
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestAuthIntegration:
    """Интеграционные тесты для процесса аутентификации"""

    def test_full_auth_flow(self, client, sample_user_data):
        """Тест полного процесса аутентификации: регистрация -> вход -> использование токена"""
        # Регистрация
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Вход
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        access_token = token_data["access_token"]

        # Использование токена для доступа к защищенному эндпоинту
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/api/v1/users/me", headers=headers)

        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.json()
        assert profile_data["email"] == sample_user_data["email"]

    def test_password_requirements(self, client):
        """Тест требований к паролю"""
        # Слишком короткий пароль
        short_password_data = {
            "email": "short@test.com",
            "username": "shorttest",
            "password": "12",
        }
        response = client.post("/api/v1/auth/register", json=short_password_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Пароль без цифр
        no_digit_password_data = {
            "email": "nodigit@test.com",
            "username": "nodigittest",
            "password": "passwordabc",
        }
        response = client.post("/api/v1/auth/register", json=no_digit_password_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_token_refresh(self, client, sample_user_data):
        """Тест обновления токена"""
        # Регистрация и вход
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        token_data = login_response.json()
        refresh_token = token_data["refresh_token"]

        # Обновление токена
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status_code == status.HTTP_200_OK
        new_token_data = refresh_response.json()
        assert "access_token" in new_token_data
        assert "refresh_token" in new_token_data

    def test_logout_invalidates_token(self, client, sample_user_data):
        """Тест что logout делает токен недействительным"""
        # Регистрация и вход
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        access_token = login_response.json()["access_token"]

        # Выход
        headers = {"Authorization": f"Bearer {access_token}"}
        logout_response = client.post("/api/v1/auth/logout", headers=headers)
        assert logout_response.status_code == status.HTTP_200_OK

        # Попытка использовать токен после logout
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_multiple_concurrent_sessions(self, client, sample_user_data):
        """Тест множественных одновременных сессий"""
        # Регистрация
        client.post("/api/v1/auth/register", json=sample_user_data)

        # Несколько входов
        tokens = []
        for _ in range(3):
            login_response = client.post(
                "/api/v1/auth/login",
                json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
            )
            assert login_response.status_code == status.HTTP_200_OK
            tokens.append(login_response.json()["access_token"])

        # Все токены должны работать
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/users/me", headers=headers)
            assert response.status_code == status.HTTP_200_OK
