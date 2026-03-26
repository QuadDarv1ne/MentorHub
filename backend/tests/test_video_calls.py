"""
Tests for video calls functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.main import app
from app.models.user import User, UserRole
from app.models.video_call import VideoCall, CallType, CallStatus
from app.utils.security import get_password_hash

client = TestClient(app)


@pytest.fixture
def test_user(db_session: Session):
    """Create test user"""
    user = User(
        email="videocall_test@example.com",
        username="videocall_test_user",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
        hashed_password=get_password_hash("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.delete(user)
    db_session.commit()


@pytest.fixture
def test_user_2(db_session: Session):
    """Create second test user"""
    user = User(
        email="videocall_test2@example.com",
        username="videocall_test_user_2",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
        hashed_password=get_password_hash("testpassword123")
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
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "testpassword123"}
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}


def test_create_one_on_one_video_call(auth_header: dict, db_session: Session, test_user_2: User):
    """Test creating 1-on-1 video call"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")
    
    response = client.post(
        "/api/v1/calls/",
        headers=auth_header,
        json={
            "participant_id": test_user_2.id,
            "title": "Test Call"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["call_type"] == "one_on_one"
    assert data["participant_id"] == test_user_2.id
    assert "agora_channel" in data
    assert "agora_token" in data
    
    # Cleanup
    db_session.delete(db_session.query(VideoCall).filter_by(id=data["id"]).first())
    db_session.commit()


def test_get_video_calls(auth_header: dict, db_session: Session):
    """Test getting video calls"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")
    
    response = client.get("/api/v1/calls/", headers=auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert "calls" in data
    assert "total" in data


def test_start_video_call(auth_header: dict, db_session: Session):
    """Test starting a video call"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")
    
    # Create a call first
    user = db_session.query(User).filter_by(email="videocall_test@example.com").first()
    call = VideoCall(
        creator_id=user.id,
        call_type=CallType.ONE_ON_ONE,
        agora_channel="test_channel",
        status=CallStatus.SCHEDULED
    )
    db_session.add(call)
    db_session.commit()
    
    response = client.post(f"/api/v1/calls/{call.id}/start", headers=auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["started_at"] is not None
    
    # Cleanup
    db_session.delete(call)
    db_session.commit()


def test_end_video_call(auth_header: dict, db_session: Session):
    """Test ending a video call"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")
    
    # Create a call
    user = db_session.query(User).filter_by(email="videocall_test@example.com").first()
    call = VideoCall(
        creator_id=user.id,
        call_type=CallType.ONE_ON_ONE,
        agora_channel="test_channel_2",
        status=CallStatus.IN_PROGRESS,
        started_at=db_session.query(func.now()).scalar()
    )
    db_session.add(call)
    db_session.commit()
    
    response = client.post(f"/api/v1/calls/{call.id}/end", headers=auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["ended_at"] is not None
    assert data["duration_seconds"] is not None
    
    # Cleanup
    db_session.delete(call)
    db_session.commit()


def test_cancel_video_call(auth_header: dict, db_session: Session):
    """Test cancelling a video call"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")
    
    # Create a call
    user = db_session.query(User).filter_by(email="videocall_test@example.com").first()
    call = VideoCall(
        creator_id=user.id,
        call_type=CallType.ONE_ON_ONE,
        agora_channel="test_channel_3",
        status=CallStatus.SCHEDULED
    )
    db_session.add(call)
    db_session.commit()
    
    response = client.delete(f"/api/v1/calls/{call.id}", headers=auth_header)
    
    assert response.status_code == 204
    
    # Verify cancelled
    db_session.refresh(call)
    assert call.status == CallStatus.CANCELLED
    
    # Cleanup
    db_session.delete(call)
    db_session.commit()


def test_join_video_call(auth_header: dict, db_session: Session):
    """Test joining a video call"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")
    
    # Create a call
    user = db_session.query(User).filter_by(email="videocall_test@example.com").first()
    call = VideoCall(
        creator_id=user.id,
        call_type=CallType.ONE_ON_ONE,
        agora_channel="test_channel_4",
        status=CallStatus.SCHEDULED
    )
    db_session.add(call)
    db_session.commit()
    
    response = client.post(f"/api/v1/calls/{call.id}/join", headers=auth_header)
    
    assert response.status_code == 200
    data = response.json()
    assert "agora_app_id" in data
    assert "agora_channel" in data
    assert "agora_token" in data
    
    # Cleanup
    db_session.delete(call)
    db_session.commit()
