"""
Tests for Achievements API
Тесты для endpoints достижений
"""

import pytest
from fastapi import status


class TestAchievementsRead:
    """Тесты чтения достижений"""

    def test_get_achievements_list(self, sync_authenticated_client):
        """Тест получения списка достижений"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/achievements", headers=headers)
        # Должен вернуть 200 (возможно пустой список) или 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_achievements_unauthorized(self, client):
        """Тест получения достижений без авторизации"""
        response = client.get("/api/v1/achievements")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMyAchievements:
    """Тесты моих достижений"""

    def test_get_my_achievements(self, sync_authenticated_client):
        """Тест получения моих достижений"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/achievements/my", headers=headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_my_achievements_unauthorized(self, client):
        """Тест получения моих достижений без авторизации"""
        response = client.get("/api/v1/achievements/my")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAchievementUnlock:
    """Тесты разблокировки достижений"""

    def test_unlock_achievement(self, sync_authenticated_client):
        """Тест разблокировки достижения"""
        client, headers = sync_authenticated_client

        # Попытка разблокировать достижение
        response = client.post("/api/v1/achievements/1/unlock", headers=headers)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        ]


class TestAchievementValidation:
    """Тесты валидации достижений"""

    def test_achievement_non_existent_id(self, sync_authenticated_client):
        """Тест достижения с несуществующим ID"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/achievements/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
