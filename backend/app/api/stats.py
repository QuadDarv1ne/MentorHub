"""
Statistics API endpoint
Provides platform statistics and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.services.cache import cache_service

router = APIRouter()


@router.get("/stats/platform")
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
    from app.models.user import User
    
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_mentors = db.query(func.count(User.id)).filter(User.is_mentor == True).scalar() or 0
    
    # Calculate active users (logged in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    stats = {
        "total_users": total_users,
        "total_mentors": total_mentors,
        "total_students": total_users - total_mentors,
        "platform_name": "MentorHub",
        "version": "1.0.0",
    }
    
    # Try to get session and course stats if models exist
    try:
        from app.api.sessions import Session as MentoringSession
        total_sessions = db.query(func.count(MentoringSession.id)).scalar() or 0
        stats["total_sessions"] = total_sessions
    except:
        pass
    
    # Cache for 5 minutes
    cache_service.set(cache_key, stats, ttl=300)
    
    return stats


@router.get("/stats/user")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
            from app.api.sessions import Session as MentoringSession
            total_sessions = db.query(func.count(MentoringSession.id)).filter(
                MentoringSession.mentor_id == current_user.id
            ).scalar() or 0
            
            completed_sessions = db.query(func.count(MentoringSession.id)).filter(
                and_(
                    MentoringSession.mentor_id == current_user.id,
                    MentoringSession.status == 'completed'
                )
            ).scalar() or 0
            
            stats["mentor_stats"] = {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
            }
        except:
            pass
    
    return stats


@router.get("/stats/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
        
        total_courses = db.query(func.count(Progress.id.distinct())).filter(
            Progress.user_id == current_user.id
        ).scalar() or 0
        
        completed = db.query(func.count(Progress.id)).filter(
            and_(
                Progress.user_id == current_user.id,
                Progress.completed == True
            )
        ).scalar() or 0
        
        stats["total_courses"] = total_courses
        stats["completed"] = completed
        stats["in_progress"] = total_courses - completed
    except:
        pass
    
    # Try to get session stats
    try:
        from app.api.sessions import Session as MentoringSession
        
        total_sessions = db.query(func.count(MentoringSession.id)).filter(
            MentoringSession.student_id == current_user.id
        ).scalar() or 0
        
        upcoming = db.query(func.count(MentoringSession.id)).filter(
            and_(
                MentoringSession.student_id == current_user.id,
                MentoringSession.status.in_(['pending', 'confirmed'])
            )
        ).scalar() or 0
        
        completed_sessions = db.query(func.count(MentoringSession.id)).filter(
            and_(
                MentoringSession.student_id == current_user.id,
                MentoringSession.status == 'completed'
            )
        ).scalar() or 0
        
        stats["total_sessions"] = total_sessions
        stats["upcoming_sessions"] = upcoming
        stats["completed_sessions"] = completed_sessions
    except:
        pass
    
    return stats
