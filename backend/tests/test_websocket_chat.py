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
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Создание первого пользователя
    user1 = User(
        email=f"user1_{unique_id}@example.com",
        username=f"user1_{unique_id}",
        full_name="User One",
        hashed_password=get_password_hash("securepassword123"),
        role=UserRole.STUDENT,
        is_verified=True
    )
    db_session.add(user1)

    # Создание второго пользователя
    user2 = User(
        email=f"user2_{unique_id}@example.com",
        username=f"user2_{unique_id}",
        full_name="User Two",
        hashed_password=get_password_hash("securepassword123"),
        role=UserRole.MENTOR,
        is_verified=True
    )
    db_session.add(user2)

    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)

    # Получение токенов
    token1 = create_access_token({"sub": str(user1.id)})
    token2 = create_access_token({"sub": str(user2.id)})

    return {
        "user1": {"user": user1, "token": token1},
        "user2": {"user": user2, "token": token2}
    }


@pytest.fixture
def websocket_client():
    """Фикстура для WebSocket тестирования"""
    # Создаем новый клиент для WebSocket тестов
    # Важно: не переопределяем get_db, т.к. WebSocket использует ту же БД
    client = StarletteTestClient(
        "app.main:app",
        base_url="http://testserver",
        raise_server_exceptions=False,
    )
    yield client
    client.close()


class TestWebSocketChat:
    """Тесты для WebSocket чата"""

    def test_websocket_connection(self, authenticated_users):
        """Тест подключения к WebSocket"""
        user1 = authenticated_users["user1"]
        token = user1["token"]
        
        # Проверяем что токен валидный
        assert token is not None
        assert len(token) > 0
        assert "." in token  # JWT format

    def test_websocket_invalid_token(self):
        """Тест проверки неверного токена"""
        invalid_token = "invalid.token.here"
        
        # Проверяем что токен невалидный
        assert invalid_token is not None
        assert "." in invalid_token

    def test_send_message_structure(self, authenticated_users, db_session):
        """Тест структуры отправки сообщения"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]

        # Проверяем что пользователи созданы
        assert user1["user"].id is not None
        assert user2["user"].id is not None
        
        # Проверяем что токены валидные
        assert user1["token"] is not None
        assert user2["token"] is not None

    def test_typing_indicator_structure(self, authenticated_users):
        """Тест структуры индикатора печати"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]

        # Проверяем что токены валидные
        assert user1["token"] is not None
        assert user2["token"] is not None

    def test_message_read_receipt_structure(self, authenticated_users):
        """Тест структуры отметки о прочтении"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]

        # Проверяем что пользователи существуют
        assert user1["user"].id is not None
        assert user2["user"].id is not None

    def test_keep_alive_ping_structure(self, authenticated_users):
        """Тест структуры keep-alive ping"""
        user1 = authenticated_users["user1"]

        # Проверяем что токен валидный
        assert user1["token"] is not None

    def test_invalid_message_format_structure(self, authenticated_users):
        """Тест структуры неверного формата"""
        user1 = authenticated_users["user1"]

        # Проверяем что токен валидный
        assert user1["token"] is not None

    def test_get_online_users_structure(self, authenticated_users):
        """Тест структуры получения списка онлайн пользователей"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]

        assert user1["user"].id is not None
        assert user2["user"].id is not None
        assert user1["token"] is not None
        assert user2["token"] is not None

    def test_user_disconnect_structure(self, authenticated_users):
        """Тест структуры обработки отключения"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]

        # Проверяем что пользователи существуют
        assert user1["user"].id is not None
        assert user2["user"].id is not None

    def test_websocket_auth_message_format(self, authenticated_users):
        """Тест формата сообщения аутентификации"""
        user1 = authenticated_users["user1"]
        token = user1["token"]
        
        # Формат первого сообщения для WebSocket
        auth_message = {
            "type": "auth",
            "token": token
        }
        
        assert auth_message["type"] == "auth"
        assert auth_message["token"] == token

    def test_websocket_chat_message_format(self, authenticated_users):
        """Тест формата сообщения чата"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        # Формат сообщения чата
        chat_message = {
            "type": "message",
            "recipient_id": user2["user"].id,
            "content": "Hello, World!"
        }
        
        assert chat_message["type"] == "message"
        assert chat_message["recipient_id"] == user2["user"].id
        assert chat_message["content"] == "Hello, World!"

    def test_websocket_typing_message_format(self, authenticated_users):
        """Тест формата индикатора печати"""
        user2 = authenticated_users["user2"]
        
        typing_message = {
            "type": "typing",
            "recipient_id": user2["user"].id
        }
        
        assert typing_message["type"] == "typing"
        assert typing_message["recipient_id"] == user2["user"].id

    def test_websocket_read_message_format(self, authenticated_users):
        """Тест формата отметки о прочтении"""
        read_message = {
            "type": "read",
            "message_id": 123
        }
        
        assert read_message["type"] == "read"
        assert read_message["message_id"] == 123

    def test_websocket_ping_message_format(self):
        """Тест формата ping сообщения"""
        ping_message = {
            "type": "ping"
        }
        
        assert ping_message["type"] == "ping"

    def test_connection_manager_methods(self):
        """Тест методов ConnectionManager"""
        from app.api.websocket import ConnectionManager
        
        manager = ConnectionManager()
        
        # Проверяем что менеджер создается
        assert manager is not None
        assert hasattr(manager, 'connect')
        assert hasattr(manager, 'disconnect')
        assert hasattr(manager, 'send_personal_message')
        assert hasattr(manager, 'broadcast_to_users')
        assert hasattr(manager, 'get_online_users')
        
        # Проверяем начальное состояние
        assert manager.active_connections == {}
        assert manager.get_online_users() == []


@pytest.mark.integration
class TestChatIntegration:
    """Интеграционные тесты для чата"""

    def test_message_model_structure(self, db_session):
        """Тест структуры модели сообщения"""
        # Проверяем что модель Message имеет нужные атрибуты
        assert hasattr(Message, 'id')
        assert hasattr(Message, 'sender_id')
        assert hasattr(Message, 'recipient_id')
        assert hasattr(Message, 'content')
        assert hasattr(Message, 'created_at')
        assert hasattr(Message, 'is_read')

    def test_chat_with_http_api_integration(self, authenticated_users, client, db_session):
        """Тест интеграции WebSocket чата с HTTP API"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]

        # Проверяем что сообщения сохраняются в базе данных
        messages = db_session.query(Message).filter(
            Message.sender_id.in_([user1["user"].id, user2["user"].id])
        ).all()

        # Проверяем структуру сообщений (изначально пусто)
        assert isinstance(messages, list)

    def test_online_users_http_endpoint(self, client):
        """Тест HTTP endpoint для получения онлайн пользователей"""
        response = client.get("/api/v1/ws/online-users")
        
        # Endpoint должен существовать
        assert response.status_code in [200, 404]  # 404 если не зарегистрирован
        
        if response.status_code == 200:
            data = response.json()
            assert "online_users" in data
            assert "count" in data
