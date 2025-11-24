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
    res = client.post("/api/v1/progress", json={"course_id": 200, "progress_percent": 10})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_progress_lifecycle(client, sample_user_data):
    token = register_and_login(client, sample_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    # create progress
    res = client.post(
        "/api/v1/progress", json={"course_id": 200, "lesson_id": 1, "progress_percent": 25}, headers=headers
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["course_id"] == 200
    assert data["progress_percent"] == 25

    # update same progress record
    res2 = client.post(
        "/api/v1/progress", json={"course_id": 200, "lesson_id": 1, "progress_percent": 60}, headers=headers
    )
    assert res2.status_code == status.HTTP_201_CREATED
    data2 = res2.json()
    assert data2["id"] == data["id"]
    assert data2["progress_percent"] == 60

    # list my progress
    list_res = client.get("/api/v1/users/me/progress", headers=headers)
    assert list_res.status_code == status.HTTP_200_OK
    items = list_res.json()
    assert any(item["course_id"] == 200 for item in items)

    # aggregate (no errors)
    agg = client.get("/api/v1/courses/200/progress/aggregate")
    assert agg.status_code == status.HTTP_200_OK
