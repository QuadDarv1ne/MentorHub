"""
Tests for Mentor Search API
"""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models.mentor import Mentor
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


@pytest.fixture
def test_mentors(db_session: Session):
    """Create test mentors with different attributes"""
    import uuid
    run_id = str(uuid.uuid4())[:8]

    # Create users
    users = []
    for i in range(5):
        user = User(
            email=f"mentor_{run_id}_{i}@test.com",
            username=f"mentor_username_{run_id}_{i}",
            full_name=f"Mentor {i}",
            hashed_password=get_password_hash("testpass123"),
            role=UserRole.MENTOR,
            is_active=True
        )
        db_session.add(user)
        users.append(user)

    db_session.flush()

    # Create mentors with different attributes
    mentors_data = [
        {
            "user_id": users[0].id,
            "specialization": "Python",
            "bio": "Expert Python developer",
            "experience_years": 5,
            "hourly_rate": 50,
            "rating": 4.8,
            "total_sessions": 20,
            "is_available": True
        },
        {
            "user_id": users[1].id,
            "specialization": "JavaScript",
            "bio": "Frontend specialist",
            "experience_years": 3,
            "hourly_rate": 40,
            "rating": 4.5,
            "total_sessions": 15,
            "is_available": True
        },
        {
            "user_id": users[2].id,
            "specialization": "Python",
            "bio": "Backend and DevOps",
            "experience_years": 8,
            "hourly_rate": 80,
            "rating": 4.9,
            "total_sessions": 30,
            "is_available": False
        },
        {
            "user_id": users[3].id,
            "specialization": "Java",
            "bio": "Enterprise Java developer",
            "experience_years": 10,
            "hourly_rate": 100,
            "rating": 4.7,
            "total_sessions": 25,
            "is_available": True
        },
        {
            "user_id": users[4].id,
            "specialization": "React",
            "bio": "React and TypeScript expert",
            "experience_years": 4,
            "hourly_rate": 60,
            "rating": 4.6,
            "total_sessions": 18,
            "is_available": True
        }
    ]

    mentors = []
    for data in mentors_data:
        mentor = Mentor(**data)
        db_session.add(mentor)
        mentors.append(mentor)

    db_session.commit()
    return mentors


def test_search_mentors_by_query(client, test_mentors):
    """Test searching mentors by text query"""
    response = client.get("/api/v1/mentors/search?query=Python")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 2  # 2 Python mentors


def test_search_mentors_by_specialization(client, test_mentors):
    """Test filtering mentors by specialization"""
    response = client.get("/api/v1/mentors/search?specialization=JavaScript")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["specialization"] == "JavaScript"


def test_search_mentors_by_price_range(client, test_mentors):
    """Test filtering mentors by price range"""
    response = client.get("/api/v1/mentors/search?min_rate=40&max_rate=60")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["data"]) >= 2

    for mentor in data["data"]:
        assert 40 <= mentor["hourly_rate"] <= 60


def test_search_mentors_by_experience(client, test_mentors):
    """Test filtering mentors by experience"""
    response = client.get("/api/v1/mentors/search?min_experience=5")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    for mentor in data["data"]:
        assert mentor["experience_years"] >= 5


def test_search_mentors_available_only(client, test_mentors):
    """Test filtering only available mentors"""
    response = client.get("/api/v1/mentors/search?is_available=true")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    for mentor in data["data"]:
        assert mentor["is_available"] is True


def test_search_mentors_sort_by_rating(client, test_mentors):
    """Test sorting mentors by rating"""
    response = client.get("/api/v1/mentors/search?sort_by=rating&sort_order=desc")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Check descending order
    ratings = [m["rating"] for m in data["data"]]
    assert ratings == sorted(ratings, reverse=True)


def test_search_mentors_sort_by_price(client, test_mentors):
    """Test sorting mentors by price"""
    response = client.get("/api/v1/mentors/search?sort_by=price&sort_order=asc")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Check ascending order
    prices = [m["hourly_rate"] for m in data["data"]]
    assert prices == sorted(prices)


def test_search_mentors_pagination(client, test_mentors):
    """Test pagination in search results"""
    # Page 1
    response = client.get("/api/v1/mentors/search?page=1&page_size=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data["data"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] == 5

    # Page 2
    response = client.get("/api/v1/mentors/search?page=2&page_size=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data["data"]) == 2
    assert data["page"] == 2


def test_get_specializations(client, test_mentors):
    """Test getting list of all specializations"""
    response = client.get("/api/v1/mentors/specializations")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert "Python" in data
    assert "JavaScript" in data
    assert "Java" in data
    assert "React" in data


def test_get_top_rated_mentors(client, test_mentors):
    """Test getting top rated mentors"""
    response = client.get("/api/v1/mentors/top-rated?limit=3")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) <= 3

    # Check descending order by rating
    ratings = [m["rating"] for m in data]
    assert ratings == sorted(ratings, reverse=True)


def test_search_mentors_combined_filters(client, test_mentors):
    """Test combining multiple filters"""
    response = client.get(
        "/api/v1/mentors/search?"
        "min_rate=40&max_rate=80&"
        "min_experience=3&"
        "is_available=true&"
        "sort_by=rating&sort_order=desc"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    for mentor in data["data"]:
        assert 40 <= mentor["hourly_rate"] <= 80
        assert mentor["experience_years"] >= 3
        assert mentor["is_available"] is True

    # Check sorting
    ratings = [m["rating"] for m in data["data"]]
    assert ratings == sorted(ratings, reverse=True)


def test_search_mentors_no_results(client, test_mentors):
    """Test search with no matching results"""
    response = client.get("/api/v1/mentors/search?specialization=Rust")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data["data"]) == 0
    assert data["total"] == 0


def test_search_mentors_invalid_sort_field(client, test_mentors):
    """Test search with invalid sort field (should use default)"""
    response = client.get("/api/v1/mentors/search?sort_by=invalid_field")

    assert response.status_code == status.HTTP_200_OK
    # Should default to rating sort
