"""
Pydantic схемы для прогресса пользователей
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, conint


class ProgressCreate(BaseModel):
    course_id: int = Field(..., description="Stepik course id")
    lesson_id: int | None = Field(None, description="Stepik lesson id")
    progress_percent: Annotated[int, conint(ge=0, le=100)] = Field(..., description="Progress percentage from 0 to 100")
    completed: bool | None = Field(False, description="Whether the lesson/course is completed")


class ProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    course_id: int
    lesson_id: int | None
    progress_percent: int
    completed: bool
    created_at: datetime
    updated_at: datetime | None


class ProgressAggregate(BaseModel):
    course_id: int
    average_progress: float
    completed_count: int
