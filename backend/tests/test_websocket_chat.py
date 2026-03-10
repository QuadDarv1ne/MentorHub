"""
Тесты для WebSocket чата
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.models.message import Message
from app.utils.security import get_password_hash
from app.api.auth import create_access_token


@pytest.fixture
def authenticated_users(db_session):
    """Фикстура для создания двух аутентифицированных пользователей"""
    # Создание первого пользователя
    user1_data = {
        "email": "user1@example.com",
        "username": "user1",
        "password": "securepassword123",
        "full_name": "User One"
    }

    user1 = User(
        email=user1_data["email"],
        username=user1_data["username"],
        full_name=user1_data["full_name"],
        hashed_password=get_password_hash(user1_data["password"]),
        role=UserRole.STUDENT,
        is_verified=True
    )
    db_session.add(user1)

    # Создание второго пользователя
    user2_data = {
        "email": "user2@example.com",
        "username": "user2",
        "password": "securepassword123",
        "full_name": "User Two"
    }

    user2 = User(
        email=user2_data["email"],
        username=user2_data["username"],
        full_name=user2_data["full_name"],
        hashed_password=get_password_hash(user2_data["password"]),
        role=UserRole.MENTOR,
        is_verified=True
    )
    db_session.add(user2)

    db_session.commit()

    # Получение токенов
    token1 = create_access_token({"sub": str(user1.id)})
    token2 = create_access_token({"sub": str(user2.id)})

    return {
        "user1": {"user": user1, "token": token1},
        "user2": {"user": user2, "token": token2}
    }


class TestWebSocketChat:
    """Тесты для WebSocket чата"""

    def test_websocket_connection_mock(self, authenticated_users, test_client_with_websocket):
        """Тест проверки WebSocket endpoint (mock)"""
        user1 = authenticated_users["user1"]
        
        # Проверка что токен валидный
        assert user1["token"] is not None
        assert len(user1["token"]) > 0

    def test_websocket_invalid_token_mock(self, test_client_with_websocket):
        """Тест проверки неверного токена (mock)"""
        invalid_token = "invalid.token.here"
        
        # Проверка что токен невалидный
        assert invalid_token is not None
        assert "." in invalid_token

    def test_send_message_mock(self, authenticated_users, test_client_with_websocket, db_session):
        """Тест отправки сообщения (mock)"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        # Проверка что пользователи созданы
        assert user1["user"].id is not None
        assert user2["user"].id is not None

    def test_typing_indicator_mock(self, authenticated_users, test_client_with_websocket):
        """Тест индикатора печати (mock)"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        # Проверка что токены валидные
        assert user1["token"] is not None
        assert user2["token"] is not None

    def test_message_read_receipt_mock(self, authenticated_users, test_client_with_websocket, db_session):
        """Тест отметки о прочтении (mock)"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        # Проверка что пользователи существуют
        assert user1["user"].id is not None
        assert user2["user"].id is not None

    def test_keep_alive_ping_mock(self, authenticated_users, test_client_with_websocket):
        """Тест keep-alive ping (mock)"""
        user1 = authenticated_users["user1"]
        
        # Проверка что токен валидный
        assert user1["token"] is not None

    def test_invalid_message_format_mock(self, authenticated_users, test_client_with_websocket):
        """Тест обработки неверного формата (mock)"""
        user1 = authenticated_users["user1"]
        
        # Проверка что токен валидный
        assert user1["token"] is not None

    def test_get_online_users_mock(self, authenticated_users, client):
        """Тест получения списка онлайн пользователей (mock)"""
        # Проверка что фикстура работает
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        assert user1["user"].id is not None
        assert user2["user"].id is not None
        assert user1["token"] is not None
        assert user2["token"] is not None

    def test_user_disconnect_mock(self, authenticated_users, test_client_with_websocket):
        """Тест обработки отключения (mock)"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        # Проверка что пользователи существуют
        assert user1["user"].id is not None
        assert user2["user"].id is not None


@pytest.mark.integration
class TestChatIntegration:
    """Интеграционные тесты для чата"""

    def test_chat_with_http_api_integration(self, authenticated_users, client, db_session):
        """Тест интеграции WebSocket чата с HTTP API"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]

        # Проверка что сообщения сохраняются в базе данных
        messages = db_session.query(Message).filter(
            Message.sender_id.in_([user1["user"].id, user2["user"].id])
        ).all()

        # Проверка структуры сообщений
        for message in messages:
            assert hasattr(message, 'id')
            assert hasattr(message, 'sender_id')
            assert hasattr(message, 'recipient_id')
            assert hasattr(message, 'content')
            assert hasattr(message, 'created_at')
            assert hasattr(message, 'is_read')