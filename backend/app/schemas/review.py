"""
Pydantic схемы для отзывов
"""

from datetime import datetime

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, conint


class ReviewCreate(BaseModel):
    rating: Annotated[int, conint(ge=1, le=5)] = Field(..., description="Rating from 1 to 5")
    comment: str | None = Field(None, max_length=2000)


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_name: str | None = None
    course_id: int | None = None
    reviewed_id: int | None = None
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime | None


class ReviewAggregate(BaseModel):
    course_id: int
    average_rating: float
    total_reviews: int


class ReviewCreateGeneric(BaseModel):
    """Create a review for a mentor (optionally tied to a session/course)"""
    rating: Annotated[int, conint(ge=1, le=5)] = Field(..., description="Rating from 1 to 5")
    comment: str | None = Field(None, max_length=2000)
    reviewed_id: int | None = Field(None, description="ID of the mentor being reviewed")
    session_id: int | None = Field(None, description="ID of the session (for validation)")
