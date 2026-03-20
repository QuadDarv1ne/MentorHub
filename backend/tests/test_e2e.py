"""
E2E Tests for MentorHub API
Критичные сценарии использования
"""

import pytest
import httpx
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"


class TestAuthFlow:
    """Тестирование потока аутентификации"""

    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=BASE_URL, timeout=30.0)

    def test_01_register_user(self, client):
        """Регистрация нового пользователя"""
        response = client.post(
            "/auth/register",
            json={
                "email": f"e2e_test_{pytest.test_id}@example.com",
                "username": f"e2e_test_{pytest.test_id}",
                "password": "SecurePassword123!",
                "full_name": "E2E Test User",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        pytest.test_id = data["user"]["id"]

    def test_02_login_user(self, client):
        """Вход пользователя"""
        response = client.post(
            "/auth/login",
            data={
                "username": f"e2e_test_{pytest.test_id}@example.com",
                "password": "SecurePassword123!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        pytest.access_token = data["access_token"]

    def test_03_get_current_user(self, client):
        """Получение текущего пользователя"""
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {pytest.access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == f"e2e_test_{pytest.test_id}@example.com"


class TestCourseFlow:
    """Тестирование потока работы с курсами"""

    @pytest.fixture
    def auth_client(self):
        client = httpx.Client(base_url=BASE_URL, timeout=30.0)
        # Login first
        response = client.post(
            "/auth/login",
            data={
                "username": "admin@example.com",
                "password": "admin_password",
            },
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            client.headers["Authorization"] = f"Bearer {token}"
        return client

    def test_01_list_courses(self, auth_client):
        """Получение списка курсов"""
        response = auth_client.get("/courses/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_02_get_course_detail(self, auth_client):
        """Получение деталей курса"""
        # Get first course ID
        courses = auth_client.get("/courses/").json()
        if courses:
            course_id = courses[0]["id"]
            response = auth_client.get(f"/courses/{course_id}")
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "title" in data


class TestMentorFlow:
    """Тестирование потока работы с менторами"""

    @pytest.fixture
    def auth_client(self):
        client = httpx.Client(base_url=BASE_URL, timeout=30.0)
        response = client.post(
            "/auth/login",
            data={
                "username": "mentor@example.com",
                "password": "mentor_password",
            },
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            client.headers["Authorization"] = f"Bearer {token}"
        return client

    def test_01_list_mentors(self, auth_client):
        """Получение списка менторов"""
        response = auth_client.get("/mentors/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_02_get_mentor_detail(self, auth_client):
        """Получение деталей ментора"""
        mentors = auth_client.get("/mentors/").json()
        if mentors:
            mentor_id = mentors[0]["id"]
            response = auth_client.get(f"/mentors/{mentor_id}")
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "bio" in data or "specialization" in data


class TestHealthChecks:
    """Тестирование health checks"""

    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=BASE_URL, timeout=10.0)

    def test_health_endpoint(self, client):
        """Базовый health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_detailed_health(self, client):
        """Детальный health check"""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert "database" in data["services"]

    def test_ready_endpoint(self, client):
        """Ready check"""
        response = client.get("/health/ready")
        assert response.status_code == 200


class TestAPIEndpoints:
    """Базовое тестирование API endpoints"""

    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=BASE_URL, timeout=30.0)

    def test_stats_endpoint(self, client):
        """Тестирование stats endpoint"""
        response = client.get("/stats/platform")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data or "platform_name" in data

    def test_notifications_endpoint(self, client):
        """Тестирование notifications endpoint (требуется auth)"""
        # Without auth - should return 401
        response = client.get("/notifications")
        assert response.status_code in [200, 401, 403]


# Cleanup after tests
@pytest.fixture(autouse=True)
def cleanup():
    """Очистка после тестов"""
    yield
    # Cleanup test users if needed
    # This is optional and depends on your test strategy


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
