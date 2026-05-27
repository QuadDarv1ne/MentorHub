"""
Pydantic схемы для достижений
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AchievementCreate(BaseModel):
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None


class AchievementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    earned_at: datetime


class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
