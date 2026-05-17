"""
Pydantic схемы для отзывов
"""

from datetime import datetime
from pydantic import BaseModel, Field, conint, ConfigDict
from typing import Optional


class ReviewCreate(BaseModel):
    rating: conint(ge=1, le=5) = Field(..., description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=2000)


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    user_name: Optional[str] = None
    course_id: Optional[int] = None
    reviewed_id: Optional[int] = None
    rating: int
    comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class ReviewAggregate(BaseModel):
    course_id: int
    average_rating: float
    total_reviews: int


class ReviewCreateGeneric(BaseModel):
    """Create a review for a mentor (optionally tied to a session/course)"""
    rating: conint(ge=1, le=5) = Field(..., description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=2000)
    reviewed_id: Optional[int] = Field(None, description="ID of the mentor being reviewed")
    session_id: Optional[int] = Field(None, description="ID of the session (for validation)")
