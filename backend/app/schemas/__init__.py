"""
Pydantic схемы
Все схемы для запросов и ответов
"""

from app.schemas.chat_room import (
    AddMemberRequest,
    ChatMessageCreate,
    ChatMessageListResponse,
    ChatMessageResponse,
    ChatMessageUpdate,
    ChatRoomCreate,
    ChatRoomResponse,
    ChatRoomUpdate,
    ChatRoomWithMembersResponse,
    RemoveMemberRequest,
)
from app.schemas.common import MessageResponse, PaginationParams
from app.schemas.course import (
    CourseCreate,
    CourseEnrollmentCreate,
    CourseEnrollmentResponse,
    CourseEnrollmentUpdate,
    CourseResponse,
    CourseUpdate,
    LessonCreate,
    LessonResponse,
    LessonUpdate,
)
from app.schemas.review import ReviewAggregate, ReviewCreate, ReviewRead
from app.schemas.user import UserCreate, UserResponse, UserUpdate

__all__ = [
    "PaginationParams",
    "MessageResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "ReviewCreate",
    "ReviewRead",
    "ReviewAggregate",
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "LessonCreate",
    "LessonUpdate",
    "LessonResponse",
    "CourseEnrollmentCreate",
    "CourseEnrollmentUpdate",
    "CourseEnrollmentResponse",
    "ChatRoomCreate",
    "ChatRoomUpdate",
    "ChatRoomResponse",
    "ChatRoomWithMembersResponse",
    "ChatMessageCreate",
    "ChatMessageUpdate",
    "ChatMessageResponse",
    "ChatMessageListResponse",
    "AddMemberRequest",
    "RemoveMemberRequest",
]
