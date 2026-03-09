"""
Тесты health check endpoints
Тесты для проверки здоровья приложения
"""

import pytest
from fastapi import status


class TestHealthCheck:
    """Тесты базовых health check endpoints"""

    def test_health_check_success(self, client):
        """Тест успешной проверки здоровья"""
        response = client.get("/api/v1/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
        assert "database" in data["services"]

    def test_health_check_detailed(self, client):
        """Тест детальной проверки здоровья"""
        response = client.get("/api/v1/health/detailed")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "services" in data
        assert "system" in data

    def test_readiness_check(self, client):
        """Тест проверки готовности приложения"""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ready"
        assert "timestamp" in data

    def test_liveness_check(self, client):
        """Тест проверки работоспособности приложения"""
        response = client.get("/api/v1/health/live")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data

    def test_database_health(self, client):
        """Тест проверки здоровья базы данных"""
        response = client.get("/api/v1/health/database")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "database_version" in data or "error" not in data
        assert "timestamp" in data


class TestHealthCheckWithAdmin:
    """Тесты health check endpoints с авторизацией админа"""

    def test_health_check_with_admin_token(self, client, create_user, authenticated_headers):
        """Тест health check с токеном админа"""
        # Создаём админа
        admin_data = {
            "email": "admin@example.com",
            "username": "adminuser",
            "password": "AdminPass123!",
            "full_name": "Admin User",
        }
        admin = create_user(
            email=admin_data["email"],
            username=admin_data["username"],
            password=admin_data["password"],
            role="admin"
        )

        # Вход как админ
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": admin_data["email"], "password": admin_data["password"]},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Проверка health endpoint
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == status.HTTP_200_OK
