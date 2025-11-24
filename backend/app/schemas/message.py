"""
Схемы сообщений
Pydantic схемы для операций с сообщениями
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from app.schemas.user import UserResponse


class MessageBase(BaseModel):
    """Базовая схема сообщения"""

    content: str = Field(..., min_length=1, max_length=10000)


class MessageCreate(MessageBase):
    """Схема для создания сообщения"""

    sender_id: int
    recipient_id: int


class MessageUpdate(BaseModel):
    """Схема для обновления сообщения"""

    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    is_read: Optional[bool] = None


class MessageResponse(MessageBase):
    """Схема ответа с данными сообщения"""

    id: int
    sender_id: int
    recipient_id: int
    is_read: bool
    created_at: datetime
    updated_at: datetime

    # Relations
    # sender: Optional[UserResponse] = None
    # recipient: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
