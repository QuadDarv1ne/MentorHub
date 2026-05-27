"""
Схемы для видеозвонков
Pydantic схемы для Agora integration
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class VideoCallCreate(BaseModel):
    """Создание видеозвонка"""

    participant_id: Optional[int] = None  # Для 1-on-1
    room_id: Optional[int] = None  # Для групповых
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class VideoCallUpdate(BaseModel):
    """Обновление видеозвонка"""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class VideoCallResponse(BaseModel):
    """Ответ с данными звонка"""

    id: int
    creator_id: int
    creator_username: Optional[str] = None
    participant_id: Optional[int] = None
    participant_username: Optional[str] = None
    call_type: str
    room_id: Optional[int] = None
    room_name: Optional[str] = None
    agora_channel: str
    agora_token: Optional[str] = None
    agora_app_id: Optional[str] = None
    status: str
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
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

    calls: List[VideoCallResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
