"""
Роуты для отзывов о курсах
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import get_db, get_current_user, get_current_user_optional
from app.schemas.review import ReviewCreate, ReviewRead, ReviewAggregate
from app.schemas.common import PaginatedResponse
from app.models import Review, User

router = APIRouter()


@router.post("/courses/{course_id}/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(
    course_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверяем, не оставлял ли пользователь уже отзыв для этого курса
    existing = db.query(Review).filter(Review.course_id == course_id, Review.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Вы уже оставили отзыв для этого курса")

    review = Review(
        user_id=current_user.id,
        course_id=course_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.get("/courses/{course_id}/reviews", response_model=PaginatedResponse[ReviewRead])
def list_reviews(
    course_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional),
):
    # Пагинация
    total = db.query(Review).filter(Review.course_id == course_id).count()
    items = (
        db.query(Review)
        .filter(Review.course_id == course_id)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse.create(items, total, page, page_size)


@router.get("/courses/{course_id}/reviews/aggregate", response_model=ReviewAggregate)
def aggregate_reviews(course_id: int, db: Session = Depends(get_db)):
    r = db.query(func.avg(Review.rating).label("avg"), func.count(Review.id).label("total")).filter(Review.course_id == course_id).first()
    avg = float(r.avg) if r and r.avg is not None else 0.0
    total = int(r.total) if r and r.total else 0

    return ReviewAggregate(course_id=course_id, average_rating=round(avg, 2), total_reviews=total)
