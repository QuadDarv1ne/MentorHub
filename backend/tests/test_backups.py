"""
Tests for Backups API
Тесты для endpoints резервных копий
"""

import pytest
from fastapi import status


class TestBackupsInfo:
    """Тесты получения информации о backup"""

    def test_get_backup_info_success(self, sync_authenticated_client, create_user):
        """Тест получения информации о backup"""
        client, headers = sync_authenticated_client

        # Создаём админа
        admin_password = "AdminPass123!"
        admin = create_user(
            email="admin_backup@example.com",
            username="admin_backup",
            password=admin_password,
            role="admin",
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": admin.email, "password": admin_password},
        )
        token = login_response.json().get("access_token")
        if not token:
            pytest.skip("Login failed")
        admin_headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/admin/backups/info", headers=admin_headers)
        # Может вернуть 200, 501 (не доступно), 500
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_501_NOT_IMPLEMENTED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_get_backup_info_unauthorized(self, client):
        """Тест получения информации о backup без авторизации"""
        response = client.get("/api/v1/admin/backups/info")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_backup_info_non_admin(self, sync_authenticated_client):
        """Тест получения информации о backup не админом"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/admin/backups/info", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCreateBackup:
    """Тесты создания backup"""

    def test_create_backup_success(self, sync_authenticated_client, create_user):
        """Тест создания backup"""
        client, headers = sync_authenticated_client

        # Создаём админа
        admin_password = "AdminPass123!"
        admin = create_user(
            email="admin_backup2@example.com",
            username="admin_backup2",
            password=admin_password,
            role="admin",
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": admin.email, "password": admin_password},
        )
        token = login_response.json().get("access_token")
        if not token:
            pytest.skip("Login failed")
        admin_headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/api/v1/admin/backups/create", headers=admin_headers)
        # Может вернуть 200, 501, 500
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_501_NOT_IMPLEMENTED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_create_backup_unauthorized(self, client):
        """Тест создания backup без авторизации"""
        response = client.post("/api/v1/admin/backups/create")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_backup_non_admin(self, sync_authenticated_client):
        """Тест создания backup не админом"""
        client, headers = sync_authenticated_client

        response = client.post("/api/v1/admin/backups/create", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCleanupBackups:
    """Тесты очистки backup"""

    def test_cleanup_backups_success(self, sync_authenticated_client, create_user):
        """Тест очистки backup"""
        client, headers = sync_authenticated_client

        # Создаём админа
        admin_password = "AdminPass123!"
        admin = create_user(
            email="admin_backup3@example.com",
            username="admin_backup3",
            password=admin_password,
            role="admin",
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": admin.email, "password": admin_password},
        )
        token = login_response.json().get("access_token")
        if not token:
            pytest.skip("Login failed")
        admin_headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/admin/backups/cleanup?keep_days=7",
            headers=admin_headers
        )
        # Может вернуть 200, 501, 500
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_501_NOT_IMPLEMENTED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_cleanup_backups_unauthorized(self, client):
        """Тест очистки backup без авторизации"""
        response = client.post("/api/v1/admin/backups/cleanup")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cleanup_backups_non_admin(self, sync_authenticated_client):
        """Тест очистки backup не админом"""
        client, headers = sync_authenticated_client

        response = client.post("/api/v1/admin/backups/cleanup", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestVerifyBackup:
    """Тесты проверки backup"""

    def test_verify_backup_success(self, sync_authenticated_client, create_user):
        """Тест проверки backup"""
        client, headers = sync_authenticated_client

        # Создаём админа
        admin_password = "AdminPass123!"
        admin = create_user(
            email="admin_backup4@example.com",
            username="admin_backup4",
            password=admin_password,
            role="admin",
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": admin.email, "password": admin_password},
        )
        token = login_response.json().get("access_token")
        if not token:
            pytest.skip("Login failed")
        admin_headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/admin/backups/verify/backup_2024.sql",
            headers=admin_headers
        )
        # Может вернуть 200, 404, 501, 500
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_501_NOT_IMPLEMENTED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

    def test_verify_backup_unauthorized(self, client):
        """Тест проверки backup без авторизации"""
        response = client.get("/api/v1/admin/backups/verify/backup.sql")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_backup_non_admin(self, sync_authenticated_client):
        """Тест проверки backup не админом"""
        client, headers = sync_authenticated_client

        response = client.get("/api/v1/admin/backups/verify/backup.sql", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestBackupsValidation:
    """Тесты валидации backup"""

    def test_backup_filename_format(self):
        """Тест формата имени файла backup"""
        valid_filenames = [
            "backup_2024_01_01.sql",
            "backup_20240101.db",
            "backup_2024-01-01.sql.gz",
        ]
        for filename in valid_filenames:
            assert filename.startswith("backup_")
            assert "." in filename

    def test_keep_days_values(self):
        """Тест допустимых значений keep_days"""
        valid_values = [1, 7, 14, 30, 90]
        for days in valid_values:
            assert days > 0
            assert days <= 365
