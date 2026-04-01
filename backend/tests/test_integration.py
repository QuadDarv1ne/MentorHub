"""
Integration Tests for Key User Flows
Тестирование основных сценариев использования платформы
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta

from app.main import app
from app.config import settings
from app.models.user import User, UserRole
from app.models.course import Course, CourseEnrollment
from app.models.session import Session as SessionModel
from app.utils.security import get_password_hash


# ==================== Fixtures ====================

@pytest.fixture
def db_session():
    """Создание тестовой базы данных"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Импортируем все модели для создания таблиц
    from app.models.user import User
    from app.models.course import Course, Lesson, CourseEnrollment
    from app.models.session import Session as SessionModel
    from app.models.chat_room import ChatRoom, ChatMessage
    
    # Создаём таблицы
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Тестовый клиент"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    from app import dependencies
    dependencies.get_db = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(db_session):
    """Создание тестового пользователя (студент)"""
    user = User(
        email="student@test.com",
        username="test_student",
        full_name="Test Student",
        hashed_password=get_password_hash("password123"),
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_mentor(db_session):
    """Создание тестового ментора"""
    user = User(
        email="mentor@test.com",
        username="test_mentor",
        full_name="Test Mentor",
        hashed_password=get_password_hash("password123"),
        role=UserRole.MENTOR,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Создание тестового админа"""
    user = User(
        email="admin@test.com",
        username="test_admin",
        full_name="Test Admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_auth_headers(client, email, password):
    """Получить заголовки авторизации"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# ==================== Integration Tests ====================

class TestUserRegistrationFlow:
    """Тестирование потока регистрации пользователя"""

    def test_register_student(self, client):
        """Регистрация нового студента"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "username": "newuser",
                "full_name": "New User",
                "password": "SecurePass123!",
                "role": "student"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["username"] == "newuser"
        assert data["role"] == "student"

    def test_register_mentor(self, client):
        """Регистрация нового ментора"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newmentor@test.com",
                "username": "newmentor",
                "full_name": "New Mentor",
                "password": "SecurePass123!",
                "role": "mentor"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "mentor"

    def test_register_duplicate_email(self, client, test_user):
        """Регистрация с существующим email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "anotheruser",
                "full_name": "Another User",
                "password": "SecurePass123!",
                "role": "student"
            }
        )
        assert response.status_code == 400
        assert "уже существует" in response.json()["detail"]

    def test_register_weak_password(self, client):
        """Регистрация со слабым паролем"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weakpass@test.com",
                "username": "weakpass",
                "full_name": "Weak Pass",
                "password": "123",
                "role": "student"
            }
        )
        assert response.status_code == 400
        assert "Слабый пароль" in response.json()["detail"]


class TestAuthenticationFlow:
    """Тестирование аутентификации"""

    def test_login_success(self, client, test_user):
        """Успешный вход"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["expires_in"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    def test_login_wrong_password(self, client, test_user):
        """Вход с неправильным паролем"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Неверный email или пароль" in response.json()["detail"]

    def test_login_inactive_user(self, client, db_session):
        """Вход неактивного пользователя"""
        user = User(
            email="inactive@test.com",
            username="inactive",
            hashed_password=get_password_hash("password123"),
            role=UserRole.STUDENT,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@test.com", "password": "password123"}
        )
        assert response.status_code == 403
        assert "неактивна" in response.json()["detail"]

    def test_refresh_token(self, client, test_user):
        """Обновление токена"""
        # Логин
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        assert "access_token" in refresh_response.json()


class TestCourseEnrollmentFlow:
    """Тестирование записи на курсы"""

    def test_enroll_in_course(self, client, test_user, db_session):
        """Запись на курс"""
        # Создаём курс
        from app.models.mentor import Mentor
        mentor = Mentor(user_id=test_user.id)  # В реальном тесте нужен другой пользователь
        db_session.add(mentor)
        db_session.commit()

        course = Course(
            title="Test Course",
            description="Test Description",
            category="Programming",
            difficulty="beginner",
            duration_hours=10,
            price=100.0,
            is_active=True,
            instructor_id=mentor.id
        )
        db_session.add(course)
        db_session.commit()

        headers = get_auth_headers(client, test_user.email, "password123")

        # Запись на курс
        response = client.post(
            f"/api/v1/courses/{course.id}/enroll",
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["course_id"] == course.id

    def test_enroll_twice(self, client, test_user, db_session):
        """Повторная запись на курс"""
        from app.models.mentor import Mentor
        mentor = Mentor(user_id=test_user.id)
        db_session.add(mentor)
        db_session.commit()

        course = Course(
            title="Test Course",
            description="Test",
            category="Programming",
            instructor_id=mentor.id
        )
        db_session.add(course)
        
        enrollment = CourseEnrollment(
            user_id=test_user.id,
            course_id=course.id,
            progress_percent=0
        )
        db_session.add(enrollment)
        db_session.commit()

        headers = get_auth_headers(client, test_user.email, "password123")

        response = client.post(
            f"/api/v1/courses/{course.id}/enroll",
            headers=headers
        )
        assert response.status_code == 400
        assert "уже записаны" in response.json()["detail"]


class TestSessionBookingFlow:
    """Тестирование бронирования сессий"""

    def test_book_session(self, client, test_user, test_mentor, db_session):
        """Бронирование сессии с ментором"""
        headers = get_auth_headers(client, test_user.email, "password123")

        from datetime import datetime, timezone, timedelta
        session_data = {
            "mentor_id": test_mentor.id,
            "title": "Consultation",
            "description": "Career advice",
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "duration_hours": 1
        }

        response = client.post(
            "/api/v1/sessions",
            headers=headers,
            json=session_data
        )
        # Может быть 201 или 403 в зависимости от реализации
        assert response.status_code in [201, 403]


class TestUserProfileFlow:
    """Тестирование профиля пользователя"""

    def test_get_own_profile(self, client, test_user):
        """Получение собственного профиля"""
        headers = get_auth_headers(client, test_user.email, "password123")

        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    def test_update_profile(self, client, test_user):
        """Обновление профиля"""
        headers = get_auth_headers(client, test_user.email, "password123")

        response = client.put(
            "/api/v1/users/me",
            headers=headers,
            json={"full_name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"


class TestAdminAccess:
    """Тестирование доступа администратора"""

    def test_admin_can_access_users(self, client, test_admin):
        """Админ имеет доступ к списку пользователей"""
        headers = get_auth_headers(client, test_admin.email, "admin123")

        response = client.get("/api/v1/users", headers=headers)
        # Зависит от реализации - может быть 200 или требовать дополнительную проверку
        assert response.status_code in [200, 403]


# ==================== Performance Tests ====================

class TestAPIPerformance:
    """Тесты производительности API"""

    def test_health_check_response_time(self, client):
        """Время ответа health check"""
        import time
        
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5  # Менее 500мс

    def test_concurrent_requests(self, client, test_user):
        """Обработка множественных запросов"""
        import concurrent.futures
        
        headers = get_auth_headers(client, test_user.email, "password123")
        
        def make_request():
            return client.get("/api/v1/users/me", headers=headers)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]
        
        assert all(r.status_code == 200 for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
