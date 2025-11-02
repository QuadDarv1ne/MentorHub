"""
Authentication Tests
Tests for auth endpoints
"""

import pytest
from fastapi import status

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


class TestRegistration:
    """Tests for user registration"""
    
    def test_register_success(self, client, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert "password" not in data
        assert data["role"] == "student"
    
    def test_register_duplicate_email(self, client, db_session, sample_user_data):
        """Test registration with duplicate email"""
        # Create existing user
        existing_user = User(
            email=sample_user_data["email"],
            username="existinguser",
            hashed_password=get_password_hash(sample_user_data["password"]),
            role=UserRole.STUDENT,
        )
        db_session.add(existing_user)
        db_session.commit()
        
        # Try to register with same email
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_invalid_data(self, client):
        """Test registration with invalid data"""
        invalid_data = {
            "email": "not-an-email",
            "username": "ab",  # Too short
            "password": "123",  # Too short
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Tests for user login"""
    
    def test_login_success(self, client, db_session, sample_user_data):
        """Test successful login"""
        # Register user first
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials"""
        login_data = {
            "email": sample_user_data["email"],
            "password": "wrongpassword",
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword",
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestAuthIntegration:
    """Integration tests for authentication flow"""
    
    def test_full_auth_flow(self, client, sample_user_data):
        """Test complete authentication flow: register -> login -> use token"""
        # Register
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/api/v1/users/me", headers=headers)
        
        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.json()
        assert profile_data["email"] == sample_user_data["email"]

