"""
Тесты для отзывов о курсах
Покрывает создание отзыва, попытку дублирования, получение списка и агрегирования рейтинга.
"""

import pytest
from fastapi import status


def register_and_login(client, sample_user_data):
    # зарегистрируем и получим токен
    r = client.post("/api/v1/auth/register", json=sample_user_data)
    assert r.status_code == status.HTTP_201_CREATED
    login = client.post(
        "/api/v1/auth/login", json={"email": sample_user_data["email"], "password": sample_user_data["password"]}
    )
    assert login.status_code == status.HTTP_200_OK
    return login.json()["access_token"]


def test_create_review_requires_auth(client):
    res = client.post("/api/v1/courses/101/reviews", json={"rating": 5, "comment": "Great"})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_review_lifecycle(client, sample_user_data):
    token = register_and_login(client, sample_user_data)
    headers = {"Authorization": f"Bearer {token}"}
    course_id = 101

    # create review
    res = client.post(
        f"/api/v1/courses/{course_id}/reviews", json={"rating": 5, "comment": "Nice course"}, headers=headers
    )
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["rating"] == 5
    assert data["comment"] == "Nice course"
    assert "user_name" in data

    # duplicate review should fail
    res2 = client.post(f"/api/v1/courses/{course_id}/reviews", json={"rating": 4}, headers=headers)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST

    # list reviews
    list_res = client.get(f"/api/v1/courses/{course_id}/reviews")
    assert list_res.status_code == status.HTTP_200_OK
    page = list_res.json()
    assert page["total"] == 1
    assert page["data"][0]["id"] == data["id"]

    # aggregate
    agg = client.get(f"/api/v1/courses/{course_id}/reviews/aggregate")
    assert agg.status_code == status.HTTP_200_OK
    agg_data = agg.json()
    assert agg_data["total_reviews"] == 1
    assert float(agg_data["average_rating"]) == 5.0
