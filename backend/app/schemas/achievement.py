"""
Pydantic схемы для достижений
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AchievementCreate(BaseModel):
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None


class AchievementRead(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    earned_at: datetime

    class Config:
        from_attributes = True


class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None