"""
Pydantic схемы
Все схемы для запросов и ответов
"""

from app.schemas.common import PaginationParams, MessageResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.review import ReviewCreate, ReviewRead, ReviewAggregate
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, LessonCreate, LessonUpdate, LessonResponse, CourseEnrollmentCreate, CourseEnrollmentUpdate, CourseEnrollmentResponse
from app.schemas.chat_room import (
    ChatRoomCreate, ChatRoomUpdate, ChatRoomResponse, ChatRoomWithMembersResponse,
    ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse, ChatMessageListResponse,
    AddMemberRequest, RemoveMemberRequest,
)

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