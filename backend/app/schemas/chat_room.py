"""
Схемы для чат-комнат
Pydantic схемы для групповых чатов
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRoomBase(BaseModel):
    """Базовая схема чат-комнаты"""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_private: bool = False


class ChatRoomCreate(ChatRoomBase):
    """Создание чат-комнаты"""

    course_id: int | None = None


class ChatRoomUpdate(BaseModel):
    """Обновление чат-комнаты"""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_private: bool | None = None


class ChatRoomResponse(BaseModel):
    """Ответ с данными чат-комнаты"""

    id: int
    name: str
    description: str | None = None
    created_by: int
    is_private: bool
    course_id: int | None = None
    created_at: datetime
    updated_at: datetime
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ChatRoomWithMembersResponse(ChatRoomResponse):
    """Чат-комната с участниками"""

    members: list[dict] = []
    creator_username: str


class ChatMessageBase(BaseModel):
    """Базовая схема сообщения"""

    content: str = Field(..., min_length=1, max_length=10000)
    attachment_url: str | None = None
    attachment_type: str | None = None


class ChatMessageCreate(ChatMessageBase):
    """Создание сообщения"""

    room_id: int
    parent_message_id: int | None = None


class ChatMessageUpdate(BaseModel):
    """Обновление сообщения"""

    content: str | None = Field(None, min_length=1, max_length=10000)


class ChatMessageResponse(BaseModel):
    """Ответ с сообщением"""

    id: int
    room_id: int
    sender_id: int
    sender_username: str
    sender_avatar: str | None = None
    content: str
    is_edited: bool
    is_deleted: bool
    attachment_url: str | None = None
    attachment_type: str | None = None
    parent_message_id: int | None = None
    created_at: datetime
    updated_at: datetime
    replies_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ChatMessageListResponse(BaseModel):
    """Список сообщений"""

    messages: list[ChatMessageResponse]
    has_more: bool = False

    model_config = ConfigDict(from_attributes=True)


class AddMemberRequest(BaseModel):
    """Добавление участника"""

    user_id: int


class RemoveMemberRequest(BaseModel):
    """Удаление участника"""

    user_id: int
