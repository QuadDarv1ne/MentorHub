"""
Admin API endpoints for user management and platform administration.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin, get_pagination
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminUserResponse,
    AdminUserListResponse,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
    PlatformStatsResponse,
)
from app.schemas.common import PaginationParams, MessageResponse
from app.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: Optional[str] = Query(default=None, description="Filter by role: student, mentor, admin"),
    status: Optional[str] = Query(default=None, description="Filter by status: active, inactive"),
    search: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Search by name or email"),
    sort_by: str = Query(default="created_at", regex="^(created_at|email|role|full_name)$"),
    sort_order: str = Query(default="desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User)

    if role:
        query = query.filter(User.role == UserRole(role))

    if status == "active":
        query = query.filter(User.is_active == True)
    elif status == "inactive":
        query = query.filter(User.is_active == False)

    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    total = query.count()
    sort_column = getattr(User, sort_by, User.created_at)
    order = desc(sort_column) if sort_order == "desc" else sort_column.asc()
    users = query.order_by(order).offset((page - 1) * page_size).limit(page_size).all()

    return AdminUserListResponse(
        items=[AdminUserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.put("/users/{user_id}/role", response_model=AdminUserResponse)
async def update_user_role(
    user_id: int,
    body: UpdateUserRoleRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = body.role
    db.commit()
    db.refresh(user)
    logger.info(f"Admin {current_user.id} changed user {user_id} role to {body.role.value}")
    return AdminUserResponse.model_validate(user)


@router.put("/users/{user_id}/status", response_model=AdminUserResponse)
async def update_user_status(
    user_id: int,
    body: UpdateUserStatusRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own status")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = body.is_active
    db.commit()
    db.refresh(user)
    logger.info(f"Admin {current_user.id} changed user {user_id} active status to {body.is_active}")
    return AdminUserResponse.model_validate(user)


@router.get("/stats/platform", response_model=PlatformStatsResponse)
async def get_platform_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    analytics = AnalyticsService(db)
    stats = analytics.get_platform_stats()

    total_users = db.query(User).count()
    total_admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    new_users_today = db.query(User).filter(
        func.date(User.created_at) == func.current_date()
    ).count()

    from app.models.session import Session as MentorSession, SessionStatus
    active_sessions_now = db.query(MentorSession).filter(
        MentorSession.status == SessionStatus.IN_PROGRESS
    ).count()

    return PlatformStatsResponse(
        total_users=stats.get("total_users", total_users),
        total_students=stats.get("total_students", 0),
        total_mentors=stats.get("total_mentors", 0),
        total_admins=total_admins,
        verified_users=stats.get("verified_users", 0),
        active_users=active_users,
        total_sessions=stats.get("total_sessions", 0),
        completed_sessions=stats.get("completed_sessions", 0),
        scheduled_sessions=stats.get("scheduled_sessions", 0),
        total_courses=stats.get("total_courses", 0),
        active_courses=stats.get("active_courses", 0),
        total_enrollments=stats.get("total_enrollments", 0),
        total_reviews=stats.get("total_reviews", 0),
        avg_rating=float(stats.get("avg_rating", 0.0)),
        total_revenue=float(stats.get("total_revenue", 0.0)),
        new_users_today=new_users_today,
        active_sessions_now=active_sessions_now,
    )
