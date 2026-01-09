"""
Тесты для WebSocket чата
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from fastapi import status
from fastapi.testclient import TestClient
import websockets

from app.models.user import User, UserRole
from app.models.message import Message
from app.utils.security import get_password_hash, create_access_token


class TestWebSocketChat:
    """Тесты для WebSocket чата"""

    @pytest.fixture
    def authenticated_users(self, client, db_session):
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

    @pytest.mark.asyncio
    async def test_websocket_connection_success(self, authenticated_users, test_client_with_websocket):
        """Тест успешного подключения по WebSocket"""
        user1 = authenticated_users["user1"]
        
        # Подключение по WebSocket
        ws_url = f"ws://testserver/ws/chat?token={user1['token']}"
        
        async with websockets.connect(ws_url) as websocket:
            # Получение сообщения о подключении
            response = await websocket.recv()
            data = json.loads(response)
            
            assert data["type"] == "connected"
            assert data["user_id"] == user1["user"].id
            assert data["username"] == user1["user"].username

    @pytest.mark.asyncio
    async def test_websocket_invalid_token(self, test_client_with_websocket):
        """Тест подключения с неверным токеном"""
        invalid_token = "invalid.token.here"
        ws_url = f"ws://testserver/ws/chat?token={invalid_token}"
        
        with pytest.raises(websockets.exceptions.InvalidStatusCode) as exc_info:
            async with websockets.connect(ws_url):
                pass
        
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_send_message_between_users(self, authenticated_users, test_client_with_websocket, db_session):
        """Тест отправки сообщения между пользователями"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        # Подключение обоих пользователей
        ws_url1 = f"ws://testserver/ws/chat?token={user1['token']}"
        ws_url2 = f"ws://testserver/ws/chat?token={user2['token']}"
        
        async with websockets.connect(ws_url1) as ws1:
            async with websockets.connect(ws_url2) as ws2:
                # Пропускаем сообщения о подключении
                await ws1.recv()  # connected message for user1
                await ws2.recv()  # connected message for user2
                
                # Пользователь 1 отправляет сообщение пользователю 2
                message_data = {
                    "type": "message",
                    "recipient_id": user2["user"].id,
                    "content": "Hello from user1!"
                }
                
                await ws1.send(json.dumps(message_data))
                
                # Пользователь 2 получает сообщение
                response = await ws2.recv()
                received_data = json.loads(response)
                
                assert received_data["type"] == "message"
                assert received_data["sender_id"] == user1["user"].id
                assert received_data["recipient_id"] == user2["user"].id
                assert received_data["content"] == "Hello from user1!"
                
                # Проверка в базе данных
                message = db_session.query(Message).filter(
                    Message.sender_id == user1["user"].id,
                    Message.recipient_id == user2["user"].id
                ).first()
                
                assert message is not None
                assert message.content == "Hello from user1!"

    @pytest.mark.asyncio
    async def test_typing_indicator(self, authenticated_users, test_client_with_websocket):
        """Тест индикатора печати"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        ws_url1 = f"ws://testserver/ws/chat?token={user1['token']}"
        ws_url2 = f"ws://testserver/ws/chat?token={user2['token']}"
        
        async with websockets.connect(ws_url1) as ws1:
            async with websockets.connect(ws_url2) as ws2:
                # Пропускаем сообщения о подключении
                await ws1.recv()
                await ws2.recv()
                
                # Пользователь 1 отправляет индикатор печати
                typing_data = {
                    "type": "typing",
                    "recipient_id": user2["user"].id
                }
                
                await ws1.send(json.dumps(typing_data))
                
                # Пользователь 2 получает индикатор
                response = await ws2.recv()
                typing_notification = json.loads(response)
                
                assert typing_notification["type"] == "typing"
                assert typing_notification["user_id"] == user1["user"].id

    @pytest.mark.asyncio
    async def test_message_read_receipt(self, authenticated_users, test_client_with_websocket, db_session):
        """Тест отметки о прочтении сообщения"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        ws_url1 = f"ws://testserver/ws/chat?token={user1['token']}"
        ws_url2 = f"ws://testserver/ws/chat?token={user2['token']}"
        
        async with websockets.connect(ws_url1) as ws1:
            async with websockets.connect(ws_url2) as ws2:
                # Пропускаем сообщения о подключении
                await ws1.recv()
                await ws2.recv()
                
                # Пользователь 1 отправляет сообщение
                message_data = {
                    "type": "message",
                    "recipient_id": user2["user"].id,
                    "content": "Test message"
                }
                
                await ws1.send(json.dumps(message_data))
                sent_message = json.loads(await ws1.recv())
                message_id = sent_message["id"]
                
                # Пользователь 2 отправляет отметку о прочтении
                read_data = {
                    "type": "read",
                    "message_id": message_id
                }
                
                await ws2.send(json.dumps(read_data))
                
                # Пользователь 1 получает уведомление о прочтении
                read_notification = json.loads(await ws1.recv())
                
                assert read_notification["type"] == "read"
                assert read_notification["message_id"] == message_id
                assert read_notification["reader_id"] == user2["user"].id
                
                # Проверка в базе данных
                db_session.refresh(db_session.query(Message).get(message_id))
                message = db_session.query(Message).get(message_id)
                assert message.is_read is True

    @pytest.mark.asyncio
    async def test_keep_alive_ping(self, authenticated_users, test_client_with_websocket):
        """Тест keep-alive ping/pong"""
        user1 = authenticated_users["user1"]
        ws_url = f"ws://testserver/ws/chat?token={user1['token']}"
        
        async with websockets.connect(ws_url) as websocket:
            # Пропускаем сообщение о подключении
            await websocket.recv()
            
            # Отправка ping
            ping_data = {"type": "ping"}
            await websocket.send(json.dumps(ping_data))
            
            # Получение pong
            response = await websocket.recv()
            pong_data = json.loads(response)
            
            assert pong_data["type"] == "pong"

    @pytest.mark.asyncio
    async def test_invalid_message_format(self, authenticated_users, test_client_with_websocket):
        """Тест обработки неверного формата сообщения"""
        user1 = authenticated_users["user1"]
        ws_url = f"ws://testserver/ws/chat?token={user1['token']}"
        
        async with websockets.connect(ws_url) as websocket:
            # Пропускаем сообщение о подключении
            await websocket.recv()
            
            # Отправка сообщения без обязательных полей
            invalid_data = {
                "type": "message",
                "content": "Missing recipient_id"
                # recipient_id отсутствует
            }
            
            await websocket.send(json.dumps(invalid_data))
            
            # Получение ошибки
            response = await websocket.recv()
            error_data = json.loads(response)
            
            assert error_data["type"] == "error"
            assert "Missing" in error_data["message"]

    @pytest.mark.asyncio
    async def test_get_online_users(self, authenticated_users, client):
        """Тест получения списка онлайн пользователей"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        # Подключение пользователей через WebSocket
        ws_url1 = f"ws://testserver/ws/chat?token={user1['token']}"
        ws_url2 = f"ws://testserver/ws/chat?token={user2['token']}"
        
        async with websockets.connect(ws_url1) as ws1:
            async with websockets.connect(ws_url2) as ws2:
                # Пропускаем сообщения о подключении
                await ws1.recv()
                await ws2.recv()
                
                # Запрос списка онлайн пользователей
                response = client.get("/api/v1/ws/online-users")
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                
                online_users = data["online_users"]
                assert user1["user"].id in online_users
                assert user2["user"].id in online_users
                assert data["count"] >= 2

    @pytest.mark.asyncio
    async def test_user_disconnect_handling(self, authenticated_users, test_client_with_websocket):
        """Тест обработки отключения пользователя"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        ws_url1 = f"ws://testserver/ws/chat?token={user1['token']}"
        ws_url2 = f"ws://testserver/ws/chat?token={user2['token']}"
        
        # Подключение первого пользователя
        async with websockets.connect(ws_url1) as ws1:
            await ws1.recv()  # connected message
            
            # Подключение второго пользователя
            async with websockets.connect(ws_url2) as ws2:
                await ws2.recv()  # connected message
                
                # Отправка сообщения от пользователя 1 к пользователю 2
                message_data = {
                    "type": "message",
                    "recipient_id": user2["user"].id,
                    "content": "Test message"
                }
                await ws1.send(json.dumps(message_data))
                
                # Получение сообщения пользователем 2
                response = await ws2.recv()
                assert json.loads(response)["type"] == "message"
                
                # Пользователь 2 отключается (выход из контекста)
            
            # После отключения пользователя 2, отправка сообщения должна работать
            # (хотя пользователь 2 его не получит)
            message_data2 = {
                "type": "message",
                "recipient_id": user2["user"].id,
                "content": "Message after disconnect"
            }
            await ws1.send(json.dumps(message_data2))
            
            # Это не должно вызвать ошибку, так как сервер должен обработать отключение


@pytest.mark.integration
class TestChatIntegration:
    """Интеграционные тесты для чата"""

    def test_chat_with_http_api_integration(self, authenticated_users, client, db_session):
        """Тест интеграции WebSocket чата с HTTP API"""
        user1 = authenticated_users["user1"]
        user2 = authenticated_users["user2"]
        
        # Отправка сообщения через HTTP API (если реализовано)
        # или тестирование взаимодействия между компонентами
        
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