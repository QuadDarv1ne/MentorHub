"""
Конфигурация pytest и фикстуры
Общие тестовые фикстуры и настройка
"""

import os

# MUST be set BEFORE any other imports
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["DEBUG"] = "False"
os.environ["RATE_LIMIT_ENABLED"] = "False"
os.environ["RATE_LIMIT_REQUESTS"] = "10000"
os.environ["RATE_LIMIT_PERIOD"] = "3600"
os.environ["CORS_ORIGINS"] = '["http://localhost:3000"]'
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

# Import and clear settings cache BEFORE importing app
import importlib
import app.config
importlib.reload(app.config)

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


# URL тестовой базы данных (SQLite для тестов)
TEST_DATABASE_URL = "sqlite:///./test.db"


# Reset settings cache after setting environment variables
import app.config as config_module
if hasattr(config_module.get_settings, 'cache_clear'):
    config_module.get_settings.cache_clear()
# Reload settings with new environment
importlib.reload(config_module)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database once per session"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Создание сессии тестовой базы данных"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Создание сессии
    session = TestingSessionLocal()

    try:
        yield session
    except Exception:
        session.rollback()
    finally:
        session.rollback()  # Rollback instead of commit to preserve data for cleanup
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Создание тестового клиента с переопределением зависимости базы данных"""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.rollback()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    """Создание асинхронного тестового клиента"""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.rollback()

    app.dependency_overrides[get_db] = override_get_db

    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Примерные данные пользователя для тестирования"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "TestPass123!",
        "full_name": "Test User",
    }


@pytest.fixture
def sample_mentor_data():
    """Примерные данные ментора для тестирования"""
    return {
        "specialization": "Python Developer",
        "experience_years": 5,
        "bio": "Experienced Python developer with 5+ years in the industry",
        "hourly_rate": 50,
        "skills": ["Python", "FastAPI", "PostgreSQL"],
    }


@pytest.fixture
def sample_course_data():
    """Примерные данные курса для тестирования"""
    return {
        "title": "Python для начинающих",
        "description": "Полный курс по Python с нуля до продвинутого уровня",
        "level": "beginner",
        "duration_hours": 40,
        "price": 99.99,
    }


@pytest.fixture
def sample_session_data():
    """Примерные данные сессии для тестирования"""
    from datetime import datetime, timedelta

    future_time = datetime.utcnow() + timedelta(days=7)
    return {
        "mentor_id": 1,
        "start_time": future_time.isoformat(),
        "duration_minutes": 60,
        "notes": "Test session",
    }


@pytest.fixture
def create_user(db_session):
    """Фикстура для создания пользователя в БД"""

    def _create_user(email, username, password, role=UserRole.STUDENT):
        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            role=role,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def test_client_with_websocket(db_session):
    """Фикстура для тестирования WebSocket с переопределением get_db"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_authenticated_client(async_client):
    """Фикстура для авторизованного асинхронного клиента - возвращает кортеж (client, headers)"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    user_data = {
        "email": f"test_{unique_id}@test.com",
        "username": f"testuser_{unique_id}",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }

    # Регистрация (201 Created)
    register_response = await async_client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201], f"Registration failed: {register_response.text}"

    # Вход
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    assert "access_token" in login_response.json(), f"access_token not in response: {login_response.json()}"
    token = login_response.json()["access_token"]
    return async_client, {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authenticated_client(async_client):
    """Фикстура для авторизованного клиента (async) - возвращает кортеж (client, headers)"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    user_data = {
        "email": f"test_{unique_id}@test.com",
        "username": f"testuser_{unique_id}",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }

    # Регистрация (201 Created)
    register_response = await async_client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201], f"Registration failed: {register_response.text}"

    # Вход
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    assert "access_token" in login_response.json(), f"access_token not in response: {login_response.json()}"
    token = login_response.json()["access_token"]
    return async_client, {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sync_authenticated_client(client):
    """Фикстура для синхронных тестов с авторизацией - возвращает кортеж (client, headers)"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    user_data = {
        "email": f"test_{unique_id}@test.com",
        "username": f"testuser_{unique_id}",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }

    # Регистрация (201 Created)
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201], f"Registration failed: {register_response.text}"

    # Вход
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    assert "access_token" in login_response.json(), f"access_token not in response: {login_response.json()}"
    token = login_response.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


@pytest.fixture
def authenticated_headers(client):
    """Фикстура только для заголовков авторизации"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    user_data = {
        "email": f"test_{unique_id}@test.com",
        "username": f"testuser_{unique_id}",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }

    # Регистрация (201 Created)
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code in [200, 201], f"Registration failed: {register_response.text}"

    # Вход
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    assert "access_token" in login_response.json(), f"access_token not in response: {login_response.json()}"
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def second_async_authenticated_client(async_client):
    """Фикстура для второго авторизованного асинхронного клиента - возвращает кортеж (client, headers)"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    user2_data = {
        "email": f"user2_{unique_id}@test.com",
        "username": f"user2test_{unique_id}",
        "password": "SecurePass123!",
        "full_name": "User Two"
    }

    # Регистрация (201 Created)
    register_response = await async_client.post("/api/v1/auth/register", json=user2_data)
    assert register_response.status_code in [200, 201], f"Registration failed: {register_response.text}"

    # Вход
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": user2_data["email"], "password": user2_data["password"]},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    assert "access_token" in login_response.json(), f"access_token not in response: {login_response.json()}"
    token = login_response.json()["access_token"]
    return async_client, {"Authorization": f"Bearer {token}"}
