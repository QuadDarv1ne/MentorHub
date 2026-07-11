"""
Pydantic схемы для достижений
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AchievementCreate(BaseModel):
    title: str
    description: str | None = None
    icon: str | None = None


class AchievementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None = None
    icon: str | None = None
    earned_at: datetime


class AchievementUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    icon: str | None = None
