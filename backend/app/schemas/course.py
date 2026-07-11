"""
Схемы курсов
Pydantic схемы для операций с курсами
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.mentor import MentorResponse
from app.schemas.user import UserResponse


class CourseBase(BaseModel):
    """Базовая схема курса"""

    title: str = Field(..., max_length=255)
    description: str | None = None
    category: str | None = Field(None, max_length=100)
    difficulty: str | None = Field(None, max_length=50)  # beginner, intermediate, advanced
    duration_hours: int = Field(0, ge=0)
    price: int = Field(0, ge=0)  # в центах/копейках
    is_active: bool = True
    thumbnail_url: str | None = Field(None, max_length=512)
    instructor_id: int


class CourseCreate(CourseBase):
    """Схема для создания курса"""


class CourseUpdate(BaseModel):
    """Схема для обновления курса"""

    title: str | None = Field(None, max_length=255)
    description: str | None = None
    category: str | None = Field(None, max_length=100)
    difficulty: str | None = Field(None, max_length=50)
    duration_hours: int | None = Field(None, ge=0)
    price: int | None = Field(None, ge=0)
    is_active: bool | None = None
    thumbnail_url: str | None = Field(None, max_length=512)
    instructor_id: int | None = None


class CourseResponse(CourseBase):
    """Схема ответа с данными курса"""

    id: int
    rating: float = 0.0
    total_reviews: int = 0
    created_at: datetime
    updated_at: datetime

    # Relations
    instructor: MentorResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class LessonBase(BaseModel):
    """Базовая схема урока"""

    course_id: int
    title: str = Field(..., max_length=255)
    description: str | None = None
    content: str | None = None
    video_url: str | None = Field(None, max_length=512)
    duration_minutes: int = Field(0, ge=0)
    order: int
    is_preview: bool = False


class LessonCreate(LessonBase):
    """Схема для создания урока"""


class LessonUpdate(BaseModel):
    """Схема для обновления урока"""

    course_id: int | None = None
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    content: str | None = None
    video_url: str | None = Field(None, max_length=512)
    duration_minutes: int | None = Field(None, ge=0)
    order: int | None = None
    is_preview: bool | None = None


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


class CourseEnrollmentUpdate(BaseModel):
    """Схема для обновления записи на курс"""

    progress_percent: int | None = Field(None, ge=0, le=100)
    completed: bool | None = None
    completed_at: datetime | None = None


class CourseEnrollmentResponse(CourseEnrollmentBase):
    """Схема ответа с данными записи на курс"""

    id: int
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    # Relations
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class CourseWithLessonsResponse(CourseResponse):
    """Схема ответа с курсом и уроками"""

    lessons: list[LessonResponse] = []


class CourseWithEnrollmentResponse(CourseResponse):
    """Схема ответа с курсом и информацией о записи"""

    enrollment: CourseEnrollmentResponse | None = None
