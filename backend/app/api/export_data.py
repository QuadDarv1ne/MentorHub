"""
User Data Collection for Export

Collects all user data for GDPR compliance export.
"""

from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.session import Session as SessionModel
from app.models.payment import Payment
from app.models.review import Review
from app.models.progress import Progress
from app.models.achievement import Achievement
from app.models.message import Message
from app.models.course import CourseEnrollment


def collect_user_data(db: Session, current_user: User) -> Dict[str, Any]:
    """
    Collect all user data for export.
    
    Includes:
    - User profile
    - Session history
    - Payment history
    - Reviews
    - Learning progress
    - Achievements
    - Messages
    - Course enrollments
    
    Returns:
        Dictionary with all user data
    """
    user_data = {
        "export_date": datetime.utcnow().isoformat(),
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role.value,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
            "bio": current_user.bio,
            "phone": current_user.phone,
            "timezone": current_user.timezone,
            "language": current_user.language,
        },
        "sessions": _collect_sessions(db, current_user.id),
        "payments": _collect_payments(db, current_user.id),
        "reviews": _collect_reviews(db, current_user.id),
        "progress": _collect_progress(db, current_user.id),
        "achievements": _collect_achievements(db, current_user.id),
        "messages": _collect_messages(db, current_user.id),
        "enrollments": _collect_enrollments(db, current_user.id),
    }
    
    return user_data


def _collect_sessions(db: Session, user_id: int) -> List[Dict]:
    """Collect user sessions (as student and mentor)."""
    sessions_query = select(SessionModel).where(
        (SessionModel.student_id == user_id) |
        (SessionModel.mentor_id == user_id)
    )
    sessions = db.execute(sessions_query).scalars().all()
    
    result = []
    for session in sessions:
        result.append({
            "id": session.id,
            "student_id": session.student_id,
            "mentor_id": session.mentor_id,
            "scheduled_at": session.scheduled_at.isoformat() if session.scheduled_at else None,
            "duration_minutes": session.duration_minutes,
            "status": session.status.value,
            "meeting_link": session.meeting_link,
            "notes": session.notes,
            "created_at": session.created_at.isoformat() if session.created_at else None,
        })
    return result


def _collect_payments(db: Session, user_id: int) -> List[Dict]:
    """Collect user payments."""
    payments_query = select(Payment).where(
        (Payment.student_id == user_id) |
        (Payment.mentor_id == user_id)
    )
    payments = db.execute(payments_query).scalars().all()
    
    result = []
    for payment in payments:
        result.append({
            "id": payment.id,
            "student_id": payment.student_id,
            "mentor_id": payment.mentor_id,
            "session_id": payment.session_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status.value,
            "payment_method": payment.payment_method,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
        })
    return result


def _collect_reviews(db: Session, user_id: int) -> List[Dict]:
    """Collect user reviews."""
    reviews_query = select(Review).where(Review.user_id == user_id)
    reviews = db.execute(reviews_query).scalars().all()
    
    result = []
    for review in reviews:
        result.append({
            "id": review.id,
            "user_id": review.user_id,
            "course_id": review.course_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.isoformat() if review.created_at else None,
        })
    return result


def _collect_progress(db: Session, user_id: int) -> List[Dict]:
    """Collect user learning progress."""
    progress_query = select(Progress).where(Progress.user_id == user_id)
    progress = db.execute(progress_query).scalars().all()
    
    result = []
    for prog in progress:
        result.append({
            "id": prog.id,
            "user_id": prog.user_id,
            "course_id": prog.course_id,
            "lesson_id": prog.lesson_id,
            "progress_percent": prog.progress_percent,
            "completed": prog.completed,
            "created_at": prog.created_at.isoformat() if prog.created_at else None,
        })
    return result


def _collect_achievements(db: Session, user_id: int) -> List[Dict]:
    """Collect user achievements."""
    achievements_query = select(Achievement).where(Achievement.user_id == user_id)
    achievements = db.execute(achievements_query).scalars().all()
    
    result = []
    for achievement in achievements:
        result.append({
            "id": achievement.id,
            "user_id": achievement.user_id,
            "achievement_id": achievement.achievement_id,
            "earned_at": achievement.earned_at.isoformat() if achievement.earned_at else None,
        })
    return result


def _collect_messages(db: Session, user_id: int, limit: int = 100) -> List[Dict]:
    """Collect user messages (sent and received)."""
    messages_query = select(Message).where(
        (Message.sender_id == user_id) |
        (Message.recipient_id == user_id)
    ).limit(limit)
    messages = db.execute(messages_query).scalars().all()
    
    result = []
    for message in messages:
        content = message.content
        if len(content) > 100:
            content = content[:100] + "..."
        
        result.append({
            "id": message.id,
            "sender_id": message.sender_id,
            "recipient_id": message.recipient_id,
            "content": content,
            "is_read": message.is_read,
            "created_at": message.created_at.isoformat() if message.created_at else None,
        })
    return result


def _collect_enrollments(db: Session, user_id: int) -> List[Dict]:
    """Collect user course enrollments."""
    enrollments_query = select(CourseEnrollment).where(CourseEnrollment.user_id == user_id)
    enrollments = db.execute(enrollments_query).scalars().all()
    
    result = []
    for enrollment in enrollments:
        result.append({
            "id": enrollment.id,
            "user_id": enrollment.user_id,
            "course_id": enrollment.course_id,
            "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
            "completed": enrollment.completed,
            "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
        })
    return result


def get_user_data_counts(db: Session, user_id: int) -> Dict[str, int]:
    """Get counts of user data records."""
    counts = {
        "sessions": db.execute(
            select(SessionModel).where(
                (SessionModel.student_id == user_id) |
                (SessionModel.mentor_id == user_id)
            )
        ).scalars().count(),
        "payments": db.execute(
            select(Payment).where(
                (Payment.student_id == user_id) |
                (Payment.mentor_id == user_id)
            )
        ).scalars().count(),
        "reviews": db.execute(
            select(Review).where(Review.user_id == user_id)
        ).scalars().count(),
        "progress": db.execute(
            select(Progress).where(Progress.user_id == user_id)
        ).scalars().count(),
        "achievements": db.execute(
            select(Achievement).where(Achievement.user_id == user_id)
        ).scalars().count(),
        "messages": db.execute(
            select(Message).where(
                (Message.sender_id == user_id) |
                (Message.recipient_id == user_id)
            )
        ).scalars().count(),
        "enrollments": db.execute(
            select(CourseEnrollment).where(CourseEnrollment.user_id == user_id)
        ).scalars().count(),
    }
    return counts
