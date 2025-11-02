"""
Pydantic схемы для прогресса пользователей
"""
from datetime import datetime
from pydantic import BaseModel, Field, conint
from typing import Optional


class ProgressCreate(BaseModel):
    course_id: int = Field(..., description="Stepik course id")
    lesson_id: Optional[int] = Field(None, description="Stepik lesson id")
    progress_percent: conint(ge=0, le=100) = Field(..., description="Progress percentage from 0 to 100")
    completed: Optional[bool] = Field(False, description="Whether the lesson/course is completed")


class ProgressRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    lesson_id: Optional[int]
    progress_percent: int
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ProgressAggregate(BaseModel):
    course_id: int
    average_progress: float
    completed_count: int
