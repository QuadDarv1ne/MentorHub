"""
Роуты для отзывов о курсах
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_current_user_optional, get_db, rate_limit_dependency
from app.models import CourseEnrollment, Review, User
from app.schemas.common import PaginatedResponse
from app.schemas.review import ReviewAggregate, ReviewCreate, ReviewCreateGeneric, ReviewRead
from app.utils.sanitization import sanitize_text_field

router = APIRouter()


@router.post("/courses/{course_id}/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(
    course_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    # Проверяем, что пользователь записан на курс
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == current_user.id,
        CourseEnrollment.course_id == course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы должны быть записаны на курс чтобы оставить отзыв"
        )

    # Создаем отзыв с обработкой race condition
    try:
        review = Review(
            user_id=current_user.id,
            course_id=course_id,
            rating=payload.rating,
            comment=sanitize_text_field(payload.comment) if payload.comment else None,
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
    except Exception as e:
        db.rollback()
        # Проверяем, не дубликат ли это (unique constraint violation)
        if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже оставили отзыв для этого курса"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании отзыва"
        )


@router.get("/courses/{course_id}/reviews", response_model=PaginatedResponse[ReviewRead])
def list_reviews(
    course_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    # Пагинация
    total = db.query(Review).filter(Review.course_id == course_id).count()
    items = (
        db.query(Review)
        .options(joinedload(Review.reviewer))
        .filter(Review.course_id == course_id)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse.create(items, total, page, page_size)


@router.get("/courses/{course_id}/reviews/aggregate", response_model=ReviewAggregate)
def aggregate_reviews(
    course_id: int,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    r = (
        db.query(func.avg(Review.rating).label("avg"), func.count(Review.id).label("total"))
        .filter(Review.course_id == course_id)
        .first()
    )
    avg = float(r.avg) if r and r.avg is not None else 0.0
    total = int(r.total) if r and r.total else 0

    return ReviewAggregate(course_id=course_id, average_rating=round(avg, 2), total_reviews=total)


@router.post("/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review_generic(
    payload: ReviewCreateGeneric,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Create a review for a mentor (optionally tied to a completed session)"""
    from app.models.mentor import Mentor
    from app.models.session import Session as MentorSession
    from app.models.session import SessionStatus

    if not payload.reviewed_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите reviewed_id (ментор)"
        )

    # If session_id provided, validate user attended that session
    if payload.session_id:
        session = db.query(MentorSession).filter(
            MentorSession.id == payload.session_id,
            MentorSession.student_id == current_user.id,
            MentorSession.status == SessionStatus.COMPLETED,
        ).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете оставить отзыв только о завершённой сессии"
            )
        # Auto-fill reviewed_id from session mentor if not provided
        if not payload.reviewed_id:
            mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
            if mentor:
                payload.reviewed_id = mentor.user_id

    # Prevent duplicate: user already reviewed this mentor
    existing = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.reviewed_id == payload.reviewed_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже оставили отзыв этому ментору"
        )

    review = Review(
        user_id=current_user.id,
        reviewed_id=payload.reviewed_id,
        course_id=None,
        rating=payload.rating,
        comment=sanitize_text_field(payload.comment) if payload.comment else None,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Update mentor rating aggregate
    mentor = db.query(Mentor).filter(Mentor.user_id == payload.reviewed_id).first()
    if mentor:
        avg = db.query(func.avg(Review.rating)).filter(Review.reviewed_id == payload.reviewed_id).scalar() or 0.0
        mentor.rating = float(avg)
        db.commit()

    return review
