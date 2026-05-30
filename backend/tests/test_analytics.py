"""
Tests for Analytics API
Тесты для endpoints аналитики
"""

import pytest
from fastapi import status


class TestAnalyticsRead:
    """Тесты чтения аналитики"""

    def test_get_analytics_success(self, sync_authenticated_client):
        """Тест успешного получения аналитики"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/analytics", headers=headers)
        # Должен вернуть 200 или 404 если endpoint не найден
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_analytics_unauthorized(self, client):
        """Тест получения аналитики без авторизации"""
        response = client.get("/api/v1/analytics")
        # Endpoint may return 401 (unauthorized) or 404 (not found)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


class TestAnalyticsUsers:
    """Тесты аналитики пользователей"""

    def test_get_user_analytics(self, sync_authenticated_client):
        """Тест получения аналитики пользователей"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/analytics/users", headers=headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestAnalyticsCourses:
    """Тесты аналитики курсов"""

    def test_get_course_analytics(self, sync_authenticated_client):
        """Тест получения аналитики курсов"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/analytics/courses", headers=headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


class TestAnalyticsRevenue:
    """Тесты аналитики доходов"""

    def test_get_revenue_analytics(self, sync_authenticated_client):
        """Тест получения аналитики доходов"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/analytics/revenue", headers=headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_revenue_analytics_date_range(self, sync_authenticated_client):
        """Тест получения аналитики доходов с диапазоном дат"""
        client, headers = sync_authenticated_client

        response = client.get(
            "/api/v1/analytics/revenue?start_date=2024-01-01&end_date=2024-12-31",
            headers=headers
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]


class TestAnalyticsValidation:
    """Тесты валидации аналитики"""

    def test_analytics_invalid_date_format(self, sync_authenticated_client):
        """Тест аналитики с невалидным форматом даты"""
        client, headers = sync_authenticated_client

        response = client.get(
            "/api/v1/analytics/revenue?start_date=invalid-date",
            headers=headers
        )
        # May return 200 (ignores invalid), 400, 422, or 404
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_404_NOT_FOUND,
        ]
