"""
End-to-End Tests
Критические пользовательские сценарии
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import User, Mentor, Session as MentorSession


class TestUserRegistrationFlow:
    """Тесты регистрации и авторизации пользователя"""
    
    @pytest.mark.asyncio
    async def test_complete_registration_flow(self, async_client: AsyncClient):
        """Полный цикл регистрации нового пользователя"""
        
        # 1. Регистрация
        registration_data = {
            "email": "newuser@test.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        assert response.status_code == 201
        user_data = response.json()
        assert user_data["email"] == registration_data["email"]
        assert "id" in user_data
        
        # 2. Авторизация
        login_data = {
            "username": registration_data["email"],
            "password": registration_data["password"]
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data
        )
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # 3. Получение профиля
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = await async_client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == registration_data["email"]
    
    @pytest.mark.asyncio
    async def test_duplicate_registration(self, async_client: AsyncClient):
        """Тест на дублирование email"""
        
        user_data = {
            "email": "duplicate@test.com",
            "password": "Pass123!",
            "full_name": "Duplicate Test"
        }
        
        # Первая регистрация - успешна
        response1 = await async_client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        assert response1.status_code == 201
        
        # Вторая регистрация - ошибка
        response2 = await async_client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        assert response2.status_code == 400


class TestMentorBookingFlow:
    """Тесты бронирования сессии с ментором"""
    
    @pytest.mark.asyncio
    async def test_complete_booking_flow(
        self,
        async_client: AsyncClient,
        authenticated_client: tuple[AsyncClient, dict]
    ):
        """Полный цикл бронирования сессии"""
        
        client, auth_data = authenticated_client
        
        # 1. Получение списка менторов
        response = await client.get("/api/v1/mentors")
        assert response.status_code == 200
        mentors = response.json()
        assert len(mentors) > 0
        mentor_id = mentors[0]["id"]
        
        # 2. Получение профиля ментора
        response = await client.get(f"/api/v1/mentors/{mentor_id}")
        assert response.status_code == 200
        mentor = response.json()
        assert mentor["id"] == mentor_id
        
        # 3. Создание сессии
        session_data = {
            "mentor_id": mentor_id,
            "scheduled_at": "2024-12-01T14:00:00",
            "duration_minutes": 60,
            "topic": "Python best practices"
        }
        
        response = await client.post(
            "/api/v1/sessions",
            json=session_data
        )
        assert response.status_code == 201
        session = response.json()
        assert session["mentor_id"] == mentor_id
        assert session["status"] == "scheduled"
        
        # 4. Получение списка своих сессий
        response = await client.get("/api/v1/sessions/my")
        assert response.status_code == 200
        sessions = response.json()
        assert any(s["id"] == session["id"] for s in sessions)
        
        # 5. Отмена сессии
        response = await client.post(
            f"/api/v1/sessions/{session['id']}/cancel"
        )
        assert response.status_code == 200
        cancelled_session = response.json()
        assert cancelled_session["status"] == "cancelled"


class TestCourseEnrollmentFlow:
    """Тесты записи на курс"""
    
    @pytest.mark.asyncio
    async def test_course_enrollment_flow(
        self,
        async_client: AsyncClient,
        authenticated_client: tuple[AsyncClient, dict]
    ):
        """Полный цикл записи на курс"""
        
        client, auth_data = authenticated_client
        
        # 1. Просмотр каталога курсов
        response = await client.get("/api/v1/courses")
        assert response.status_code == 200
        courses = response.json()
        assert len(courses) > 0
        course_id = courses[0]["id"]
        
        # 2. Просмотр деталей курса
        response = await client.get(f"/api/v1/courses/{course_id}")
        assert response.status_code == 200
        course = response.json()
        assert course["id"] == course_id
        
        # 3. Запись на курс
        response = await client.post(
            f"/api/v1/courses/{course_id}/enroll"
        )
        assert response.status_code in [200, 201]
        
        # 4. Проверка списка моих курсов
        response = await client.get("/api/v1/courses/my")
        assert response.status_code == 200
        my_courses = response.json()
        assert any(c["id"] == course_id for c in my_courses)


class TestMessagingFlow:
    """Тесты обмена сообщениями"""
    
    @pytest.mark.asyncio
    async def test_send_receive_messages(
        self,
        async_client: AsyncClient,
        authenticated_client: tuple[AsyncClient, dict],
        second_authenticated_client: tuple[AsyncClient, dict]
    ):
        """Тест отправки и получения сообщений"""
        
        client1, user1 = authenticated_client
        client2, user2 = second_authenticated_client
        
        # 1. Пользователь 1 отправляет сообщение пользователю 2
        message_data = {
            "recipient_id": user2["user"]["id"],
            "content": "Hello! Can we schedule a session?"
        }
        
        response = await client1.post(
            "/api/v1/messages",
            json=message_data
        )
        assert response.status_code == 201
        message = response.json()
        assert message["content"] == message_data["content"]
        
        # 2. Пользователь 2 получает сообщения
        response = await client2.get("/api/v1/messages")
        assert response.status_code == 200
        messages = response.json()
        assert any(m["id"] == message["id"] for m in messages)
        
        # 3. Пользователь 2 отмечает сообщение прочитанным
        response = await client2.put(
            f"/api/v1/messages/{message['id']}/read"
        )
        assert response.status_code == 200
        
        # 4. Получение истории переписки
        response = await client1.get(
            f"/api/v1/messages/conversation/{user2['user']['id']}"
        )
        assert response.status_code == 200
        conversation = response.json()
        assert len(conversation) > 0


class TestPaymentFlow:
    """Тесты платежей"""
    
    @pytest.mark.asyncio
    async def test_payment_intent_creation(
        self,
        async_client: AsyncClient,
        authenticated_client: tuple[AsyncClient, dict]
    ):
        """Тест создания платежного намерения"""
        
        client, auth_data = authenticated_client
        
        # Создание платежного намерения
        payment_data = {
            "amount": 50.00,
            "currency": "usd",
            "description": "Session payment"
        }
        
        response = await client.post(
            "/api/v1/payments/create-intent",
            json=payment_data
        )
        
        # В тестовой среде может быть недоступен Stripe
        assert response.status_code in [200, 201, 503]
        
        if response.status_code in [200, 201]:
            payment_intent = response.json()
            assert "client_secret" in payment_intent


class TestRateLimiting:
    """Тесты ограничения частоты запросов"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self, async_client: AsyncClient):
        """Тест срабатывания rate limiting"""
        
        # Делаем много запросов подряд
        responses = []
        for _ in range(150):  # Превышаем лимит в 100 запросов
            response = await async_client.get("/api/v1/courses")
            responses.append(response.status_code)
        
        # Должна быть хотя бы одна ошибка 429 (Too Many Requests)
        assert 429 in responses


class TestSecurityHeaders:
    """Тесты заголовков безопасности"""
    
    @pytest.mark.asyncio
    async def test_security_headers_present(self, async_client: AsyncClient):
        """Проверка наличия заголовков безопасности"""
        
        response = await async_client.get("/health")
        
        # Проверяем важные заголовки безопасности
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        
        assert "Content-Security-Policy" in response.headers


# Pytest fixtures
@pytest.fixture
async def authenticated_client(async_client: AsyncClient):
    """Фикстура для аутентифицированного клиента"""
    
    # Регистрация
    user_data = {
        "email": "testuser1@test.com",
        "password": "TestPass123!",
        "full_name": "Test User 1"
    }
    
    await async_client.post("/api/v1/auth/register", json=user_data)
    
    # Авторизация
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    token_data = response.json()
    
    # Создаем новый клиент с заголовком авторизации
    client = AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    
    yield client, token_data
    
    await client.aclose()


@pytest.fixture
async def second_authenticated_client(async_client: AsyncClient):
    """Фикстура для второго аутентифицированного клиента"""
    
    user_data = {
        "email": "testuser2@test.com",
        "password": "TestPass123!",
        "full_name": "Test User 2"
    }
    
    await async_client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    token_data = response.json()
    
    client = AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    
    yield client, token_data
    
    await client.aclose()
