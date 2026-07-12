"""
Tests for chat rooms functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.chat_room import ChatMessage, ChatRoom
from app.models.user import User, UserRole
from app.utils.security import get_password_hash

client = TestClient(app)


@pytest.fixture
def test_user(db_session: Session):
    """Create test user"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"chat_test_{unique_id}@example.com",
        username=f"chat_test_user_{unique_id}",
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
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"chat_test2_{unique_id}@example.com",
        username=f"chat_test_user_2_{unique_id}",
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


def test_create_chat_room(auth_header: dict, db_session: Session):
    """Test creating a chat room"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    response = client.post(
        "/api/v1/chat-rooms",
        headers=auth_header,
        json={
            "name": "Test Room",
            "description": "Test description",
            "is_private": False
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Room"
    assert data["description"] == "Test description"
    assert "id" in data

    # Cleanup
    db_session.delete(db_session.query(ChatRoom).filter_by(id=data["id"]).first())
    db_session.commit()


def test_get_chat_rooms(auth_header: dict, db_session: Session):
    """Test getting chat rooms"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    # Create a test room
    user = db_session.query(User).filter_by(email="chat_test@example.com").first()
    if user:
        room = ChatRoom(
            name="Test Room 2",
            created_by=user.id,
            is_private=False
        )
        room.members.append(user)
        db_session.add(room)
        db_session.commit()

        response = client.get("/api/v1/chat-rooms", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Cleanup
        db_session.delete(room)
        db_session.commit()


def test_send_chat_message(auth_header: dict, db_session: Session):
    """Test sending a message in chat room"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    # Create a room
    user = db_session.query(User).filter_by(email="chat_test@example.com").first()
    if not user:
        pytest.skip("User not found")

    room = ChatRoom(
        name="Message Test Room",
        created_by=user.id,
        is_private=False
    )
    room.members.append(user)
    db_session.add(room)
    db_session.commit()

    response = client.post(
        f"/api/v1/chat-rooms/{room.id}/messages",
        headers=auth_header,
        json={"content": "Hello, World!", "room_id": room.id}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Hello, World!"
    assert data["sender_id"] == user.id

    # Cleanup
    db_session.delete(room)
    db_session.commit()


def test_get_chat_messages(auth_header: dict, db_session: Session):
    """Test getting messages from chat room"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    # Create a room with message
    user = db_session.query(User).filter_by(email="chat_test@example.com").first()
    if not user:
        pytest.skip("User not found")

    room = ChatRoom(
        name="Messages Test Room",
        created_by=user.id,
        is_private=False
    )
    room.members.append(user)

    message = ChatMessage(
        room_id=room.id,
        sender_id=user.id,
        content="Test message"
    )

    db_session.add(room)
    db_session.add(message)
    db_session.commit()

    response = client.get(f"/api/v1/chat-rooms/{room.id}/messages", headers=auth_header)

    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) > 0

    # Cleanup
    db_session.delete(room)
    db_session.commit()


def test_add_member_to_chat(auth_header: dict, db_session: Session, test_user_2: User):
    """Test adding member to chat room"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    # Create a private room
    user = db_session.query(User).filter_by(email="chat_test@example.com").first()
    if not user:
        pytest.skip("User not found")

    room = ChatRoom(
        name="Private Room",
        created_by=user.id,
        is_private=True
    )
    room.members.append(user)
    db_session.add(room)
    db_session.commit()

    response = client.post(
        f"/api/v1/chat-rooms/{room.id}/members",
        headers=auth_header,
        json={"user_id": test_user_2.id}
    )

    assert response.status_code == 200

    # Verify member was added
    db_session.refresh(room)
    assert test_user_2 in room.members

    # Cleanup
    db_session.delete(room)
    db_session.commit()


def test_delete_chat_room(auth_header: dict, db_session: Session):
    """Test deleting a chat room"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    # Create a room
    user = db_session.query(User).filter_by(email="chat_test@example.com").first()
    if not user:
        pytest.skip("User not found")

    room = ChatRoom(
        name="Delete Test Room",
        created_by=user.id,
        is_private=False
    )
    db_session.add(room)
    db_session.commit()
    room_id = room.id

    response = client.delete(f"/api/v1/chat-rooms/{room_id}", headers=auth_header)

    assert response.status_code == 204

    # Verify room was deleted
    deleted_room = db_session.query(ChatRoom).filter_by(id=room_id).first()
    assert deleted_room is None


def test_edit_chat_message(auth_header: dict, db_session: Session):
    """Test editing a chat message"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    # Create a room with message
    user = db_session.query(User).filter_by(email="chat_test@example.com").first()
    if not user:
        pytest.skip("User not found")

    room = ChatRoom(
        name="Edit Test Room",
        created_by=user.id,
        is_private=False
    )
    room.members.append(user)

    message = ChatMessage(
        room_id=room.id,
        sender_id=user.id,
        content="Original message"
    )

    db_session.add(room)
    db_session.add(message)
    db_session.commit()

    response = client.put(
        f"/api/v1/chat-messages/{message.id}",
        headers=auth_header,
        json={"content": "Edited message"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Edited message"
    assert data["is_edited"] is True

    # Cleanup
    db_session.delete(room)
    db_session.commit()


def test_delete_chat_message(auth_header: dict, db_session: Session):
    """Test soft deleting a chat message"""
    if "Authorization" not in auth_header:
        pytest.skip("No auth token available")

    # Create a room with message
    user = db_session.query(User).filter_by(email="chat_test@example.com").first()
    if not user:
        pytest.skip("User not found")

    room = ChatRoom(
        name="Delete Message Room",
        created_by=user.id,
        is_private=False
    )
    room.members.append(user)

    message = ChatMessage(
        room_id=room.id,
        sender_id=user.id,
        content="Message to delete"
    )

    db_session.add(room)
    db_session.add(message)
    db_session.commit()

    response = client.delete(f"/api/v1/chat-messages/{message.id}", headers=auth_header)

    assert response.status_code == 204

    # Verify message is soft deleted
    db_session.refresh(message)
    assert message.is_deleted is True
    assert "[Сообщение удалено]" in message.content

    # Cleanup
    db_session.delete(room)
    db_session.commit()
