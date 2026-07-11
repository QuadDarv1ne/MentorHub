"""
Схемы сообщений
Pydantic схемы для операций с сообщениями
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    """Базовая схема сообщения"""

    content: str = Field(..., min_length=1, max_length=10000)


class MessageCreate(MessageBase):
    """Схема для создания сообщения"""

    sender_id: int
    recipient_id: int


class MessageUpdate(BaseModel):
    """Схема для обновления сообщения"""

    content: str | None = Field(None, min_length=1, max_length=10000)
    is_read: bool | None = None


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


class MessageWithSenderResponse(MessageResponse):
    """Расширенная схема сообщения с данными отправителя"""

    sender_username: str
    sender_avatar: str | None = None


class MessageListResponse(BaseModel):
    """Схема списка сообщений с мета-данными"""

    messages: list[MessageResponse]
    other_user: dict
    has_more: bool = False

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    """Схема диалога с пользователем"""

    user_id: int
    username: str
    avatar_url: str | None = None
    last_message: str
    last_message_time: datetime
    unread_count: int = 0
    is_from_me: bool = False

    model_config = ConfigDict(from_attributes=True)
