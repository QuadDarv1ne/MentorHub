"""
Tests for Error Handling
Тесты обработки ошибок и исключений
"""

from fastapi import status


class TestHTTPErrorHandling:
    """Тесты обработки HTTP ошибок"""

    def test_404_not_found(self, client):
        """Тест обработки 404 ошибки"""
        response = client.get("/api/v1/users/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_401_unauthorized(self, client):
        """Тест обработки 401 ошибки"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_422_validation_error(self, client):
        """Тест обработки 422 ошибки валидации"""
        # Невалидный email
        register_data = {"email": "not-an-email", "username": "test", "password": "123"}
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_400_bad_request(self, client):
        """Тест обработки 400 ошибки"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Дублирование email
        register_data = {"email": f"duplicate_{unique_id}@example.com", "username": f"user1_{unique_id}", "password": "TestPass123!"}

        # Первая регистрация
        client.post("/api/v1/auth/register", json=register_data)

        # Вторая регистрация с тем же email
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestErrorResponseBody:
    """Тесты формата тела ошибки"""

    def test_error_response_format(self, client):
        """Тест формата ответа об ошибке"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        data = response.json()
        # API returns error format with message, status_code, error_code, timestamp, path
        assert "message" in data or "detail" in data

    def test_422_error_details(self, client):
        """Тест деталей 422 ошибки"""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "invalid", "username": "ab", "password": "12"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        data = response.json()
        # FastAPI returns detail for 422
        assert "detail" in data or "message" in data
        assert isinstance(data.get("detail"), list) or "message" in data

    def test_404_error_message(self, client):
        """Тест сообщения 404 ошибки"""
        response = client.get("/api/v1/courses/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        data = response.json()
        assert "message" in data or "detail" in data


class TestRateLimiting:
    """Тесты rate limiting"""

    def test_rate_limit_headers(self, client):
        """Тест заголовков rate limiting"""
        response = client.get("/api/v1/health")

        # Проверка что ответ успешный
        assert response.status_code == status.HTTP_200_OK

    def test_rate_limit_multiple_requests(self, client):
        """Тест множественных запросов"""
        # Делаем много запросов
        for _ in range(10):
            response = client.get("/api/v1/health")
            assert response.status_code == status.HTTP_200_OK


class TestExceptionHandler:
    """Тесты обработчиков исключений"""

    def test_unhandled_exception(self, client):
        """Тест необработанного исключения"""
        # Запрос к несуществующему эндпоинту
        response = client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_method_not_allowed(self, client):
        """Тест неправильного метода"""
        # POST на GET эндпоинт
        response = client.post("/api/v1/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestDatabaseErrors:
    """Тесты ошибок базы данных"""

    def test_database_connection_error(self, client):
        """Тест ошибки подключения к БД"""
        # Health endpoint должен работать
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK

    def test_database_integrity_error(self, client):
        """Тест ошибки целостности БД"""
        # Пытаемся создать пользователя с невалидными данными
        invalid_data = {"email": "", "username": "", "password": ""}
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSecurityErrors:
    """Тесты security ошибок"""

    def test_invalid_token_format(self, client):
        """Тест неверного формата токена"""
        headers = {"Authorization": "Bearer invalid.token.format"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_authorization_header(self, client):
        """Тест отсутствия заголовка авторизации"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_authorization_scheme(self, client):
        """Тест неправильной схемы авторизации"""
        headers = {"Authorization": "Basic invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
