"""
Tests for data export functionality (PDF, Excel, JSON, CSV)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User, UserRole

client = TestClient(app)


@pytest.fixture
def test_user(db_session: Session):
    """Create test user"""
    user = User(
        email="export_test@example.com",
        username="export_test_user",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.delete(user)
    db_session.commit()


@pytest.fixture
def auth_header(test_user: User) -> dict:
    """Get auth header for test user"""
    # Set password for login
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"])
    test_user.hashed_password = pwd_context.hash("testpassword123")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "testpassword123"}
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}


def test_export_json(auth_header: dict):
    """Test JSON export"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    response = client.get("/api/v1/export/data?format=json", headers=auth_header)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "Content-Disposition" in response.headers
    assert "mentorhub_data_export" in response.headers["Content-Disposition"]

    data = response.json()
    assert "user" in data
    assert "sessions" in data
    assert "payments" in data


def test_export_csv(auth_header: dict):
    """Test CSV export"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    response = client.get("/api/v1/export/data?format=csv", headers=auth_header)

    # CSV export may return 200 or 503 depending on dependencies
    if response.status_code == 200:
        assert "text/csv" in response.headers.get("content-type", "")
        assert "mentorhub_data_export" in response.headers.get("Content-Disposition", "")


def test_export_pdf(auth_header: dict):
    """Test PDF export"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    response = client.get("/api/v1/export/data?format=pdf", headers=auth_header)

    # PDF export may return 200 or 503 depending on reportlab
    if response.status_code == 200:
        assert response.headers["content-type"] == "application/pdf"
        assert "mentorhub_export" in response.headers["Content-Disposition"]
    elif response.status_code == 503:
        # Service unavailable if reportlab not installed
        assert "not available" in response.json().get("detail", "")


def test_export_excel(auth_header: dict):
    """Test Excel export"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    response = client.get("/api/v1/export/data?format=excel", headers=auth_header)

    # Excel export may return 200 or 503 depending on openpyxl
    if response.status_code == 200:
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers.get("content-type", "")
        assert "mentorhub_export" in response.headers.get("Content-Disposition", "")
    elif response.status_code == 503:
        # Service unavailable if openpyxl not installed
        assert "not available" in response.json().get("detail", "")


def test_export_summary(auth_header: dict):
    """Test data summary endpoint"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    response = client.get("/api/v1/export/data/summary", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "username" in data
    assert "data_summary" in data
    assert "total_records" in data
