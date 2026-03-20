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
    course_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class ReviewAggregate(BaseModel):
    course_id: int
    average_rating: float
    total_reviews: int
