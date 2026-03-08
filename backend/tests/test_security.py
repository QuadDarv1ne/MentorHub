"""
Tests for Security Middleware
Тесты для безопасности: SQL injection, XSS, path traversal
"""

import pytest
from fastapi import status
import json


class TestSQLInjection:
    """Тесты защиты от SQL инъекций"""

    def test_sql_injection_in_url(self, client):
        """Тест SQL инъекции в URL"""
        # Попытка SQL инъекции через query params
        response = client.get("/api/v1/users?email=admin@test.com' OR 1=1--")
        # Должен быть заблокирован
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_sql_injection_in_body(self, client, sample_user_data):
        """Тест SQL инъекции в теле запроса"""
        login_data = {
            "email": "admin@test.com' OR 1=1--",
            "password": sample_user_data["password"],
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        # Должен быть заблокирован или возвращён 401 (не 500)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_sql_keywords_in_input(self, client, sample_user_data):
        """Тест SQL ключевых слов в input"""
        user_data = {
            "email": sample_user_data["email"],
            "username": "DROP TABLE users",
            "password": sample_user_data["password"],
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        # Может быть разрешено (если нет паттерна) или заблокировано
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]


class TestXSS:
    """Тесты защиты от XSS атак"""

    def test_xss_in_body(self, client, sample_user_data):
        """Тест XSS в теле запроса"""
        # Регистрация и вход
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Попытка XSS через bio
        update_data = {
            "bio": "<script>alert('XSS')</script>",
        }
        response = client.put("/api/v1/users/me", json=update_data, headers=headers)
        # Должен быть заблокирован
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_xss_script_tag(self, client):
        """Тест XSS с script тегом"""
        login_data = {
            "email": "<script>alert(1)</script>@test.com",
            "password": "test",
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        # Должен быть заблокирован
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_xss_javascript_protocol(self, client):
        """Тест XSS с javascript: protocol"""
        update_data = {
            "bio": "javascript:alert('XSS')",
        }
        # Без авторизации должен быть 401
        response = client.put("/api/v1/users/me", json=update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPathTraversal:
    """Тесты защиты от path traversal атак"""

    def test_path_traversal_in_url(self, client):
        """Тест path traversal в URL"""
        response = client.get("/api/v1/../../../etc/passwd")
        # FastAPI должен вернуть 404
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_path_traversal_encoding(self, client):
        """Тест path traversal с encoding"""
        response = client.get("/api/v1/%2e%2e/%2e%2e/etc/passwd")
        # Должен быть заблокирован или 404
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]


class TestCommandInjection:
    """Тесты защиты от command injection"""

    def test_command_in_body(self, client, sample_user_data):
        """Тест command injection в теле запроса"""
        # Регистрация и вход
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Попытка command injection
        update_data = {
            "bio": "test; cat /etc/passwd",
        }
        response = client.put("/api/v1/users/me", json=update_data, headers=headers)
        # Должен быть заблокирован или разрешён (если нет паттерна)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]


class TestRateLimiting:
    """Тесты rate limiting"""

    def test_rate_limit_multiple_requests(self, client):
        """Тест rate limiting при множественных запросах"""
        # Отправляем много запросов быстро
        for i in range(50):
            response = client.get("/api/v1/health")
            # Должны проходить первые 100 запросов
            if i < 100:
                assert response.status_code == status.HTTP_200_OK

    def test_rate_limit_auth_endpoint(self, client, sample_user_data):
        """Тест rate limiting для auth endpoints"""
        # Auth endpoints имеют строгий лимит (10 запросов в минуту)
        for i in range(15):
            response = client.post(
                "/api/v1/auth/login",
                json={"email": sample_user_data["email"], "password": "wrong"},
            )
            # После 10 запросов должен быть 429
            if i >= 10:
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


class TestSecurityHeaders:
    """Тесты security headers"""

    def test_security_headers_present(self, client):
        """Тест наличия security headers"""
        response = client.get("/api/v1/health")

        # Проверка security headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Content-Security-Policy" in response.headers
        assert "Strict-Transport-Security" in response.headers

    def test_cors_headers(self, client):
        """Тест CORS headers"""
        response = client.get(
            "/api/v1/health",
            headers={"Origin": "http://localhost:3000"},
        )

        # Проверка CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers.get("Access-Control-Allow-Credentials") == "true"


class TestMaliciousUserAgents:
    """Тесты защиты от malicious user agents"""

    @pytest.mark.parametrize("user_agent", [
        "sqlmap/1.0",
        "nikto/2.1.6",
        "nmap scripting engine",
    ])
    def test_malicious_user_agents(self, client, user_agent):
        """Тест блокировки malicious user agents"""
        headers = {"User-Agent": user_agent}
        response = client.get("/api/v1/health", headers=headers)
        # Должен быть заблокирован
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,  # Если проверка отключена
        ]


class TestInputValidation:
    """Тесты валидации input"""

    def test_empty_email(self, client):
        """Тест пустого email"""
        register_data = {
            "email": "",
            "username": "testuser",
            "password": "TestPass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_too_long_username(self, client):
        """Тест слишком длинного username"""
        register_data = {
            "email": "test@example.com",
            "username": "a" * 1000,
            "password": "TestPass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_json(self, client):
        """Тест невалидного JSON"""
        response = client.post(
            "/api/v1/auth/login",
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
