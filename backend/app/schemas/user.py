"""
Схемы пользователей
Pydantic схемы для операций с пользователями
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

from app.models.user import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Схема для регистрации пользователя"""
    password: str = Field(min_length=8, max_length=100)
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    """Схема для обновления профиля пользователя"""
    full_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)
    username: Optional[str] = Field(None, min_length=3, max_length=100)


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Схема ответа с токенами аутентификации"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

