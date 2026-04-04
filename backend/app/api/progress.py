"""
Роуты для трекинга прогресса пользователей
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import get_db, get_current_user, rate_limit_dependency
from app.schemas.progress import ProgressCreate, ProgressRead, ProgressAggregate
from app.models import Progress, CourseEnrollment

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/progress", response_model=ProgressRead, status_code=status.HTTP_201_CREATED)
def upsert_progress(
    payload: ProgressCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Create or update a progress record for current user"""
    # Проверяем, что пользователь записан на курс
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == current_user.id,
        CourseEnrollment.course_id == payload.course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы должны быть записаны на курс чтобы отслеживать прогресс"
        )

    # Try to find an existing record for user/course/lesson
    q = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.course_id == payload.course_id,
    )
    if payload.lesson_id is not None:
        q = q.filter(Progress.lesson_id == payload.lesson_id)
    else:
        q = q.filter(Progress.lesson_id.is_(None))

    existing = q.first()

    if existing:
        existing.progress_percent = payload.progress_percent
        existing.completed = bool(payload.completed)
        db.add(existing)
        try:
            db.commit()
            db.refresh(existing)
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating progress: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при обновлении прогресса")
        return existing

    new = Progress(
        user_id=current_user.id,
        course_id=payload.course_id,
        lesson_id=payload.lesson_id,
        progress_percent=payload.progress_percent,
        completed=bool(payload.completed or False),
    )
    db.add(new)
    try:
        db.commit()
        db.refresh(new)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating progress: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании записи прогресса")
    return new


@router.get("/users/me/progress", response_model=List[ProgressRead])
def list_my_progress(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    q = db.query(Progress).filter(Progress.user_id == current_user.id)
    if course_id:
        q = q.filter(Progress.course_id == course_id)
    items = q.order_by(Progress.updated_at.desc()).all()
    return items


@router.get("/courses/{course_id}/progress/aggregate", response_model=ProgressAggregate)
def aggregate_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    r = (
        db.query(
            func.avg(Progress.progress_percent).label("avg"),
            func.count(func.nullif(Progress.completed, False)).label("completed_count"),
        )
        .filter(Progress.course_id == course_id)
        .first()
    )
    avg = float(r.avg) if r and r.avg is not None else 0.0
    completed_count = int(r.completed_count) if r and r.completed_count else 0

    return ProgressAggregate(course_id=course_id, average_progress=round(avg, 2), completed_count=completed_count)
