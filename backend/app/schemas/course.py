"""
Схемы курсов
Pydantic схемы для операций с курсами
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

from app.schemas.user import UserResponse
from app.schemas.mentor import MentorResponse


class CourseBase(BaseModel):
    """Базовая схема курса"""

    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[str] = Field(None, max_length=50)  # beginner, intermediate, advanced
    duration_hours: int = Field(0, ge=0)
    price: int = Field(0, ge=0)  # в центах/копейках
    is_active: bool = True
    thumbnail_url: Optional[str] = Field(None, max_length=512)
    instructor_id: int


class CourseCreate(CourseBase):
    """Схема для создания курса"""
    pass


class CourseUpdate(BaseModel):
    """Схема для обновления курса"""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[str] = Field(None, max_length=50)
    duration_hours: Optional[int] = Field(None, ge=0)
    price: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    thumbnail_url: Optional[str] = Field(None, max_length=512)
    instructor_id: Optional[int] = None


class CourseResponse(CourseBase):
    """Схема ответа с данными курса"""

    id: int
    rating: float = 0.0
    total_reviews: int = 0
    created_at: datetime
    updated_at: datetime

    # Relations
    instructor: Optional[MentorResponse] = None

    model_config = ConfigDict(from_attributes=True)


class LessonBase(BaseModel):
    """Базовая схема урока"""

    course_id: int
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = Field(None, max_length=512)
    duration_minutes: int = Field(0, ge=0)
    order: int
    is_preview: bool = False


class LessonCreate(LessonBase):
    """Схема для создания урока"""
    pass


class LessonUpdate(BaseModel):
    """Схема для обновления урока"""

    course_id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = Field(None, max_length=512)
    duration_minutes: Optional[int] = Field(None, ge=0)
    order: Optional[int] = None
    is_preview: Optional[bool] = None


class LessonResponse(LessonBase):
    """Схема ответа с данными урока"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseEnrollmentBase(BaseModel):
    """Базовая схема записи на курс"""

    user_id: int
    course_id: int
    progress_percent: int = Field(0, ge=0, le=100)
    completed: bool = False


class CourseEnrollmentCreate(CourseEnrollmentBase):
    """Схема для создания записи на курс"""
    pass


class CourseEnrollmentUpdate(BaseModel):
    """Схема для обновления записи на курс"""

    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    completed: Optional[bool] = None
    completed_at: Optional[datetime] = None


class CourseEnrollmentResponse(CourseEnrollmentBase):
    """Схема ответа с данными записи на курс"""

    id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Relations
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class CourseWithLessonsResponse(CourseResponse):
    """Схема ответа с курсом и уроками"""

    lessons: List[LessonResponse] = []


class CourseWithEnrollmentResponse(CourseResponse):
    """Схема ответа с курсом и информацией о записи"""

    enrollment: Optional[CourseEnrollmentResponse] = None