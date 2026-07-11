"""
Схемы для видеозвонков
Pydantic схемы для Agora integration
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VideoCallCreate(BaseModel):
    """Создание видеозвонка"""

    participant_id: int | None = None  # Для 1-on-1
    room_id: int | None = None  # Для групповых
    title: str | None = None
    description: str | None = None
    scheduled_at: datetime | None = None


class VideoCallUpdate(BaseModel):
    """Обновление видеозвонка"""

    title: str | None = None
    description: str | None = None
    status: str | None = None


class VideoCallResponse(BaseModel):
    """Ответ с данными звонка"""

    id: int
    creator_id: int
    creator_username: str | None = None
    participant_id: int | None = None
    participant_username: str | None = None
    call_type: str
    room_id: int | None = None
    room_name: str | None = None
    agora_channel: str
    agora_token: str | None = None
    agora_app_id: str | None = None
    status: str
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    title: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgoraTokenResponse(BaseModel):
    """Ответ с токеном Agora"""

    agora_app_id: str
    agora_channel: str
    agora_token: str
    agora_uid: int


class VideoCallListResponse(BaseModel):
    """Список звонков"""

    calls: list[VideoCallResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
