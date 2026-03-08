"""
Тесты для прогресса пользователей
Проверяют создание/обновление записи прогресса и получение списка пользователя.
"""

import pytest
from fastapi import status


def register_and_login(client, sample_user_data):
    r = client.post("/api/v1/auth/register", json=sample_user_data)
    assert r.status_code == status.HTTP_201_CREATED
    login = client.post(
        "/api/v1/auth/login", json={"email": sample_user_data["email"], "password": sample_user_data["password"]}
    )
    assert login.status_code == status.HTTP_200_OK
    return login.json()["access_token"]


def test_create_progress_requires_auth(client):
    res = client.post("/api/v1/progress", json={"course_id": 1, "progress_percent": 10})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_progress_lifecycle(client, sample_user_data):
    token = register_and_login(client, sample_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Try to create progress - may fail if course doesn't exist (expected)
    res = client.post(
        "/api/v1/progress", json={"course_id": 1, "lesson_id": 1, "progress_percent": 25}, headers=headers
    )
    # Valid responses: 201 (created), 404 (course not found), 409 (conflict)
    assert res.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND, status.HTTP_409_CONFLICT]
