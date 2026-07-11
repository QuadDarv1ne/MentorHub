from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole


class AdminUserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None = None
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UpdateUserRoleRequest(BaseModel):
    role: UserRole = Field(..., description="New role for the user")


class UpdateUserStatusRequest(BaseModel):
    is_active: bool = Field(..., description="New active status for the user")


class PlatformStatsResponse(BaseModel):
    total_users: int
    total_students: int
    total_mentors: int
    total_admins: int
    verified_users: int
    active_users: int
    total_sessions: int
    completed_sessions: int
    scheduled_sessions: int
    total_courses: int
    active_courses: int
    total_enrollments: int
    total_reviews: int
    avg_rating: float
    total_revenue: float
    new_users_today: int
    active_sessions_now: int


class CourseStatItem(BaseModel):
    course_id: int
    course_title: str
    progress_percent: float
    completed: bool

    model_config = ConfigDict(from_attributes=True)


class AdminUserStatsResponse(BaseModel):
    user: AdminUserResponse
    total_sessions: int
    completed_sessions: int
    upcoming_sessions: int
    courses_enrolled: int
    course_stats: list[CourseStatItem]
    avg_rating_given: float
    avg_rating_received: float
    engagement_score: int
    last_activity: str | None = None

    model_config = ConfigDict(from_attributes=True)
