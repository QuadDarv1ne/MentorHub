"""
Схемы сессий
Pydantic схемы для операций с сессиями менторства
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum

from app.schemas.user import UserResponse
from app.schemas.mentor import MentorResponse


class SessionStatus(str, Enum):
    """Статусы сессий"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class SessionBase(BaseModel):
    """Базовая схема сессии"""
    scheduled_at: datetime
    duration_minutes: int = Field(60, ge=15, le=180)
    meeting_link: Optional[str] = Field(None, max_length=512)
    notes: Optional[str] = None


class SessionCreate(SessionBase):
    """Схема для создания сессии"""
    student_id: int
    mentor_id: int


class SessionUpdate(BaseModel):
    """Схема для обновления сессии"""
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=180)
    status: Optional[SessionStatus] = None
    meeting_link: Optional[str] = Field(None, max_length=512)
    notes: Optional[str] = None


class SessionResponse(SessionBase):
    """Схема ответа с данными сессии"""
    id: int
    student_id: int
    mentor_id: int
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    
    # Relations
    # student: Optional[UserResponse] = None
    # mentor: Optional[MentorResponse] = None
    
    model_config = ConfigDict(from_attributes=True)