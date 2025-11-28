"""
Роуты курсов
API для работы с курсами
"""

from typing import List
from sqlalchemy import func, desc
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, rate_limit_dependency, get_current_user
from app.models.review import Review
from app.models.progress import Progress
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewRead, ReviewAggregate
from app.utils.sanitization import sanitize_text_field, is_safe_string

router = APIRouter()


@router.get("/", response_model=List[ReviewRead])
async def get_courses(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список курсов (временно возвращает отзывы)"""
    # Проверка на корректность параметров пагинации
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100

    courses = db.query(Review).offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=ReviewRead)
async def get_course(course_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить информацию о курсе по ID (временно возвращает отзыв)"""
    course = db.query(Review).filter(Review.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course


@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    review: ReviewCreate, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Создать курс (временно создает отзыв)"""
    # Санитизация входных данных
    sanitized_comment = sanitize_text_field(review.comment) if review.comment else None

    # Проверка на безопасность входных данных
    if sanitized_comment and not is_safe_string(sanitized_comment):
        raise HTTPException(status_code=400, detail="Недопустимые символы в комментарии")

    # Создаем отзыв с санитизированными данными
    db_review = Review(rating=review.rating, comment=sanitized_comment)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.put("/{course_id}", response_model=ReviewRead)
async def update_course(
    course_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить курс (временно обновляет отзыв)"""
    db_review = db.query(Review).filter(Review.id == course_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Санитизация входных данных
    sanitized_data = {}
    for key, value in review.model_dump(exclude_unset=True).items():
        if key == "comment" and value is not None:
            sanitized_value = sanitize_text_field(value)
            if not is_safe_string(sanitized_value):
                raise HTTPException(status_code=400, detail="Недопустимые символы в комментарии")
            sanitized_data[key] = sanitized_value
        else:
            sanitized_data[key] = value

    # Обновляем поля
    for key, value in sanitized_data.items():
        setattr(db_review, key, value)

    db.commit()
    db.refresh(db_review)
    return db_review


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Удалить курс (временно удаляет отзыв)"""
    db_review = db.query(Review).filter(Review.id == course_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Курс не найден")

    db.delete(db_review)
    db.commit()
    return None


@router.get("/my", response_model=List[ReviewRead])
async def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить список курсов текущего пользователя (временно на основе отзывов)"""
    # Get course IDs from user's progress records
    progress_courses = db.query(Progress.course_id).filter(Progress.user_id == current_user.id).distinct().subquery()
    
    # Get reviews for those courses
    courses = db.query(Review).filter(Review.course_id.in_(progress_courses)).all()
    return courses


@router.get("/{course_id}/similar", response_model=List[ReviewAggregate])
async def get_similar_courses(
    course_id: int, limit: int = 5, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Рекомендации: похожие/популярные курсы на основе средних оценок (исключая указанный)."""
    if limit <= 0 or limit > 20:
        limit = 5

    results = (
        db.query(
            Review.course_id.label("course_id"),
            func.avg(Review.rating).label("average_rating"),
            func.count(Review.id).label("total_reviews"),
        )
        .filter(Review.course_id != course_id)
        .group_by(Review.course_id)
        .order_by(desc("average_rating"), desc("total_reviews"))
        .limit(limit)
        .all()
    )

    return [
        {
            "course_id": r.course_id,
            "average_rating": float(r.average_rating or 0.0),
            "total_reviews": int(r.total_reviews or 0),
        }
        for r in results
    ]
