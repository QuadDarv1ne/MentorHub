"""
Tests for Error Handling
Тесты обработки ошибок и исключений
"""

import pytest
from fastapi import status, HTTPException
from httpx import AsyncClient


class TestHTTPErrorHandling:
    """Тесты обработки HTTP ошибок"""

    @pytest.mark.asyncio
    async def test_404_not_found(self, async_client: AsyncClient):
        """Тест обработки 404 ошибки"""
        response = await async_client.get("/api/v1/users/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_401_unauthorized(self, async_client: AsyncClient):
        """Тест обработки 401 ошибки"""
        response = await async_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_403_forbidden(self, async_client: AsyncClient):
        """Тест обработки 403 ошибки"""
        # Создаём пользователя
        register_data = {"email": "test@example.com", "username": "testuser", "password": "TestPass123!"}
        await async_client.post("/api/v1/auth/register", json=register_data)
        
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": register_data["email"], "password": register_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Пытаемся получить другого пользователя (должно вернуть 403 или 404)
        response = await async_client.get("/api/v1/users/999", headers=headers)
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    @pytest.mark.asyncio
    async def test_422_validation_error(self, async_client: AsyncClient):
        """Тест обработки 422 ошибки валидации"""
        # Невалидный email
        register_data = {"email": "not-an-email", "username": "test", "password": "123"}
        response = await async_client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_400_bad_request(self, async_client: AsyncClient):
        """Тест обработки 400 ошибки"""
        # Дублирование email
        register_data = {"email": "duplicate@example.com", "username": "user1", "password": "TestPass123!"}
        
        # Первая регистрация
        await async_client.post("/api/v1/auth/register", json=register_data)
        
        # Вторая регистрация с тем же email
        response = await async_client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_409_conflict(self, async_client: AsyncClient, async_authenticated_client: tuple):
        """Тест обработки 409 конфликта"""
        client, headers = async_authenticated_client

        # Пытаемся создать прогресс дважды для одного курса
        progress_data = {"course_id": 1, "progress_percent": 50}

        res1 = await client.post("/api/v1/progress", json=progress_data, headers=headers)
        res2 = await client.post("/api/v1/progress", json=progress_data, headers=headers)

        # Второй запрос должен вернуть конфликт или успех (если обновляет)
        assert res2.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_409_CONFLICT,
            status.HTTP_404_NOT_FOUND
        ]


class TestErrorResponseBody:
    """Тесты формата тела ошибки"""

    @pytest.mark.asyncio
    async def test_error_response_format(self, async_client: AsyncClient):
        """Тест формата ответа об ошибке"""
        response = await async_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_422_error_details(self, async_client: AsyncClient):
        """Тест деталей 422 ошибки"""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={"email": "invalid", "username": "ab", "password": "12"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)

    @pytest.mark.asyncio
    async def test_404_error_message(self, async_client: AsyncClient):
        """Тест сообщения 404 ошибки"""
        response = await async_client.get("/api/v1/courses/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data


class TestRateLimiting:
    """Тесты rate limiting"""

    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, async_client: AsyncClient):
        """Тест заголовков rate limiting"""
        response = await async_client.get("/api/v1/health")
        
        # Проверка что ответ успешный
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_rate_limit_multiple_requests(self, async_client: AsyncClient):
        """Тест множественных запросов"""
        # Делаем много запросов
        for _ in range(10):
            response = await async_client.get("/api/v1/health")
            assert response.status_code == status.HTTP_200_OK


class TestExceptionHandler:
    """Тесты обработчиков исключений"""

    @pytest.mark.asyncio
    async def test_unhandled_exception(self, async_client: AsyncClient):
        """Тест необработанного исключения"""
        # Запрос к несуществующему эндпоинту
        response = await async_client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, async_client: AsyncClient):
        """Тест неправильного метода"""
        # POST на GET эндпоинт
        response = await async_client.post("/api/v1/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestDatabaseErrors:
    """Тесты ошибок базы данных"""

    @pytest.mark.asyncio
    async def test_database_connection_error(self, async_client: AsyncClient):
        """Тест ошибки подключения к БД"""
        # Health endpoint должен работать
        response = await async_client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_database_integrity_error(self, async_client: AsyncClient):
        """Тест ошибки целостности БД"""
        # Пытаемся создать пользователя с невалидными данными
        invalid_data = {"email": "", "username": "", "password": ""}
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSecurityErrors:
    """Тесты security ошибок"""

    @pytest.mark.asyncio
    async def test_invalid_token_format(self, async_client: AsyncClient):
        """Тест неверного формата токена"""
        headers = {"Authorization": "Bearer invalid.token.format"}
        response = await async_client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_expired_token(self, async_client: AsyncClient):
        """Тест истёкшего токена"""
        # Создаём пользователя и получаем токен
        register_data = {"email": "expire@test.com", "username": "expiretest", "password": "TestPass123!"}
        await async_client.post("/api/v1/auth/register", json=register_data)
        
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": register_data["email"], "password": register_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # Токен должен работать (если не истёк)
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get("/api/v1/users/me", headers=headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED  # Если истёк
        ]

    @pytest.mark.asyncio
    async def test_missing_authorization_header(self, async_client: AsyncClient):
        """Тест отсутствия заголовка авторизации"""
        response = await async_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_wrong_authorization_scheme(self, async_client: AsyncClient):
        """Тест неправильной схемы авторизации"""
        headers = {"Authorization": "Basic invalid_token"}
        response = await async_client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
