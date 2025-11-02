"""
Схемы менторов
Pydantic схемы для операций с менторами
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from app.schemas.user import UserResponse


class MentorBase(BaseModel):
    """Базовая схема ментора"""
    bio: Optional[str] = None
    specialization: Optional[str] = Field(None, max_length=255)
    experience_years: int = Field(0, ge=0)
    hourly_rate: int = Field(0, ge=0)  # в центах/копейках
    is_available: bool = True


class MentorCreate(MentorBase):
    """Схема для создания профиля ментора"""
    user_id: int


class MentorUpdate(MentorBase):
    """Схема для обновления профиля ментора"""
    bio: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    hourly_rate: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None


class MentorResponse(MentorBase):
    """Схема ответа с данными ментора"""
    id: int
    user_id: int
    rating: float
    total_sessions: int
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None
    
    model_config = ConfigDict(from_attributes=True)