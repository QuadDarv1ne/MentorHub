"""
Схемы сессий
Pydantic схемы для операций с сессиями менторства
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.mentor import MentorResponse
from app.schemas.payment import PaymentResponse
from app.schemas.user import UserResponse


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
    meeting_link: str | None = Field(None, max_length=512)
    notes: str | None = None


class SessionCreate(SessionBase):
    """Схема для создания сессии"""

    student_id: int
    mentor_id: int


class SessionUpdate(BaseModel):
    """Схема для обновления сессии"""

    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(None, ge=15, le=180)
    status: SessionStatus | None = None
    meeting_link: str | None = Field(None, max_length=512)
    notes: str | None = None


class SessionResponse(SessionBase):
    """Схема ответа с данными сессии"""

    id: int
    student_id: int
    mentor_id: int
    status: SessionStatus
    created_at: datetime
    updated_at: datetime

    # Relations
    student: UserResponse | None = None
    mentor: MentorResponse | None = None
    payments: list[PaymentResponse] | None = None

    model_config = ConfigDict(from_attributes=True)
