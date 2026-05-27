"""
Admin API endpoints for user management and platform administration.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.dependencies import get_current_admin, get_db
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserStatsResponse,
    CourseStatItem,
    PlatformStatsResponse,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
)
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
    sort_by: str = Query(default="created_at", pattern="^(created_at|email|role|full_name)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User)

    if role:
        query = query.filter(User.role == UserRole(role))

    if status == "active":
        query = query.filter(User.is_active.is_(True))
    elif status == "inactive":
        query = query.filter(User.is_active.is_(False))

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
    active_users = db.query(User).filter(User.is_active.is_(True)).count()
    new_users_today = db.query(User).filter(
        func.date(User.created_at) == func.current_date()
    ).count()

    from app.models.session import Session as MentorSession
    from app.models.session import SessionStatus
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


@router.get("/users/{user_id}/stats", response_model=AdminUserStatsResponse)
async def get_user_stats(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get detailed statistics for a specific user (admin only)"""
    from app.models.course import Course, CourseEnrollment
    from app.models.progress import Progress
    from app.models.review import Review
    from app.models.session import Session as MentorSession
    from app.models.session import SessionStatus

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Session stats
    total_sessions = db.query(MentorSession).filter(
        MentorSession.student_id == user_id
    ).count()
    completed_sessions = db.query(MentorSession).filter(
        MentorSession.student_id == user_id,
        MentorSession.status == SessionStatus.COMPLETED,
    ).count()
    upcoming_sessions = db.query(MentorSession).filter(
        MentorSession.student_id == user_id,
        MentorSession.status.in_([SessionStatus.SCHEDULED, SessionStatus.CONFIRMED]),
    ).count()

    # Last activity
    last_session = db.query(MentorSession).filter(
        MentorSession.student_id == user_id
    ).order_by(func.desc(MentorSession.created_at)).first()
    last_activity = last_session.created_at.isoformat() if last_session and last_session.created_at else None

    # Course stats
    enrollments = db.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == user_id
    ).all()
    course_stats = []
    for enrollment in enrollments:
        progress = db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.course_id == enrollment.course_id,
        ).first()
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if course:
            course_stats.append(CourseStatItem(
                course_id=course.id,
                course_title=course.title,
                progress_percent=float(progress.progress_percent) if progress else 0.0,
                completed=bool(progress.completed) if progress else False,
            ))

    # Review stats
    avg_rating_given = db.query(func.avg(Review.rating)).filter(
        Review.user_id == user_id
    ).scalar() or 0.0

    avg_rating_received = db.query(func.avg(Review.rating)).filter(
        Review.reviewed_id == user_id
    ).scalar() or 0.0

    # Engagement score
    sessions_count = total_sessions
    enrollments_count = len(enrollments)
    avg_progress = sum(c.progress_percent for c in course_stats) / len(course_stats) if course_stats else 0.0
    reviews_count = db.query(Review).filter(Review.user_id == user_id).count()

    # Calculate engagement score (same logic as AnalyticsService)
    engagement_score = 0
    engagement_score += min(sessions_count * 3, 30)
    engagement_score += min(enrollments_count * 5, 25)
    engagement_score += min(avg_progress * 0.3, 30)
    engagement_score += min(reviews_count * 5, 15)
    engagement_score = min(int(engagement_score), 100)

    return AdminUserStatsResponse(
        user=AdminUserResponse.model_validate(user),
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        upcoming_sessions=upcoming_sessions,
        courses_enrolled=len(enrollments),
        course_stats=course_stats,
        avg_rating_given=float(avg_rating_given),
        avg_rating_received=float(avg_rating_received),
        engagement_score=engagement_score,
        last_activity=last_activity,
    )
