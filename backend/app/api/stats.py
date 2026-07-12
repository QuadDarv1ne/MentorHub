"""
Statistics API endpoint
Provides platform statistics and analytics
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.cache import cache_service
from app.utils.cache import cached

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stats/platform")
@cached(ttl=300, key_prefix="platform_stats")
async def get_platform_stats(db: Session = Depends(get_db)):
    """
    Get overall platform statistics
    Public endpoint with caching
    """
    # Try to get from cache
    cache_key = "platform_stats"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    # Calculate stats
    from app.models.user import User, UserRole

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_mentors = db.query(func.count(User.id)).filter(User.role == UserRole.MENTOR).scalar() or 0

    stats = {
        "total_users": total_users,
        "total_mentors": total_mentors,
        "total_students": total_users - total_mentors,
        "platform_name": "MentorHub",
        "version": "1.0.0",
    }

    # Try to get session and course stats if models exist
    try:
        from app.models.session import Session as MentoringSession

        total_sessions = db.query(func.count(MentoringSession.id)).scalar() or 0
        stats["total_sessions"] = total_sessions
    except Exception as e:
        logger.debug(f"Could not load session stats: {e}")

    # Cache for 5 minutes
    cache_service.set(cache_key, stats, ttl=300)

    return stats


@router.get("/stats/user")
@cached(ttl=300, key_prefix="user_stats")
async def get_user_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current user's statistics
    """
    stats = {
        "user_id": current_user.id,
        "email": current_user.email,
        "is_mentor": current_user.is_mentor,
        "created_at": current_user.created_at,
    }

    # Add mentor-specific stats
    if current_user.is_mentor:
        try:
            from app.models.session import Session as MentoringSession

            total_sessions = (
                db.query(func.count(MentoringSession.id)).filter(MentoringSession.mentor_id == current_user.id).scalar()
                or 0
            )

            completed_sessions = (
                db.query(func.count(MentoringSession.id))
                .filter(and_(MentoringSession.mentor_id == current_user.id, MentoringSession.status == "completed"))
                .scalar()
                or 0
            )

            stats["mentor_stats"] = {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
            }
        except Exception as e:
            logger.debug(f"Could not load mentor stats: {e}")

    return stats


@router.get("/dashboard")
@cached(ttl=120, key_prefix="user_dashboard")
async def get_dashboard_for_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get dashboard statistics for current user with upcoming sessions and recent activities
    """
    try:
        from app.models.course import Course
        from app.models.progress import Progress
        from app.models.review import Review
        from app.models.session import Session as MentoringSession

        # Course stats
        total_courses = (
            db.query(func.count(Progress.id.distinct())).filter(Progress.user_id == current_user.id).scalar() or 0
        )
        completed = (
            db.query(func.count(Progress.id))
            .filter(and_(Progress.user_id == current_user.id, Progress.completed.is_(True)))
            .scalar() or 0
        )
        in_progress = total_courses - completed

        # Session stats
        total_sessions = (
            db.query(func.count(MentoringSession.id)).filter(MentoringSession.student_id == current_user.id).scalar() or 0
        )
        upcoming = (
            db.query(func.count(MentoringSession.id))
            .filter(
                and_(
                    MentoringSession.student_id == current_user.id,
                    MentoringSession.status.in_(["pending", "confirmed", "scheduled"]),
                )
            )
            .scalar() or 0
        )
        completed_sessions = (
            db.query(func.count(MentoringSession.id))
            .filter(and_(MentoringSession.student_id == current_user.id, MentoringSession.status == "completed"))
            .scalar() or 0
        )

        # Upcoming sessions (next 5)
        upcoming_sessions_list = (
            db.query(MentoringSession)
            .filter(
                and_(
                    MentoringSession.student_id == current_user.id,
                    MentoringSession.status.in_(["pending", "confirmed", "scheduled"]),
                )
            )
            .order_by(MentoringSession.scheduled_at)
            .limit(5)
            .all()
        )

        upcoming_sessions = []
        for s in upcoming_sessions_list:
            upcoming_sessions.append({
                "id": s.id,
                "mentor_id": s.mentor_id,
                "scheduled_at": s.scheduled_at.isoformat() if s.scheduled_at else None,
                "duration_minutes": s.duration_minutes,
                "status": s.status.value if hasattr(s.status, 'value') else str(s.status),
                "meeting_link": s.meeting_link,
            })

        # Recent activities (last 10 from progress, sessions, reviews)
        activities = []

        # Recent progress
        recent_progress = (
            db.query(Progress, Course.title.label('title'))
            .outerjoin(Course, Progress.course_id == Course.id)
            .filter(Progress.user_id == current_user.id)
            .order_by(Progress.updated_at.desc())
            .limit(5)
            .all()
        )
        for p, title in recent_progress:
            activities.append({
                "type": "progress",
                "title": f"Прогресс: {title or 'Курс'}",
                "detail": f"{p.progress_percent:.0f}%",
                "created_at": p.updated_at.isoformat() if p.updated_at else p.created_at.isoformat() if p.created_at else None,
            })

        # Recent completed sessions
        recent_sessions = (
            db.query(MentoringSession)
            .filter(
                and_(
                    MentoringSession.student_id == current_user.id,
                    MentoringSession.status == "completed",
                )
            )
            .order_by(MentoringSession.scheduled_at.desc())
            .limit(3)
            .all()
        )
        for s in recent_sessions:
            activities.append({
                "type": "session",
                "title": "Завершённая сессия",
                "detail": f"Длительность: {s.duration_minutes} мин",
                "created_at": s.scheduled_at.isoformat() if s.scheduled_at else None,
            })

        # Recent reviews
        recent_reviews = (
            db.query(Review)
            .filter(Review.user_id == current_user.id)
            .order_by(Review.created_at.desc())
            .limit(2)
            .all()
        )
        for r in recent_reviews:
            activities.append({
                "type": "review",
                "title": "Отзыв",
                "detail": f"Рейтинг: {r.rating}/5",
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

        # Sort activities by created_at descending, filtering out None values first
        activities_with_dates = [a for a in activities if a.get("created_at")]
        activities_without_dates = [a for a in activities if not a.get("created_at")]
        activities_with_dates.sort(key=lambda x: x["created_at"], reverse=True)
        activities = (activities_with_dates + activities_without_dates)[:10]

        return {
            "courses": {
                "total": total_courses,
                "in_progress": in_progress,
                "completed": completed,
            },
            "sessions": {
                "total": total_sessions,
                "upcoming": upcoming,
                "completed": completed_sessions,
            },
            "upcoming_sessions": upcoming_sessions,
            "recent_activities": activities,
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard data for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при загрузке данных dashboard",
        ) from e


@router.get("/stats/dashboard")
async def get_dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get dashboard statistics for current user
    Combines data from multiple sources
    """
    stats = {
        "total_courses": 0,
        "in_progress": 0,
        "completed": 0,
        "total_sessions": 0,
        "upcoming_sessions": 0,
        "completed_sessions": 0,
        "total_reviews": 0,
        "average_rating": 0.0,
    }

    # Try to get progress stats
    try:
        from app.api.progress import Progress

        total_courses = (
            db.query(func.count(Progress.id.distinct())).filter(Progress.user_id == current_user.id).scalar() or 0
        )

        completed = (
            db.query(func.count(Progress.id))
            .filter(and_(Progress.user_id == current_user.id, Progress.completed.is_(True)))
            .scalar()
            or 0
        )

        stats["total_courses"] = total_courses
        stats["completed"] = completed
        stats["in_progress"] = total_courses - completed
    except Exception as e:
        logger.debug(f"Could not load progress stats: {e}")

    # Try to get session stats
    try:
        from app.models.session import Session as MentoringSession

        total_sessions = (
            db.query(func.count(MentoringSession.id)).filter(MentoringSession.student_id == current_user.id).scalar()
            or 0
        )

        upcoming = (
            db.query(func.count(MentoringSession.id))
            .filter(
                and_(
                    MentoringSession.student_id == current_user.id,
                    MentoringSession.status.in_(["pending", "confirmed"]),
                )
            )
            .scalar()
            or 0
        )

        completed_sessions = (
            db.query(func.count(MentoringSession.id))
            .filter(and_(MentoringSession.student_id == current_user.id, MentoringSession.status == "completed"))
            .scalar()
            or 0
        )

        stats["total_sessions"] = total_sessions
        stats["upcoming_sessions"] = upcoming
        stats["completed_sessions"] = completed_sessions
    except Exception as e:
        logger.debug(f"Could not load session stats: {e}")

    return stats
