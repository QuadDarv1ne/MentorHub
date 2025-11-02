"""
Роуты курсов
API для работы с курсами
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewRead

router = APIRouter()


@router.get("/", response_model=List[ReviewRead])
async def get_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список курсов (временно возвращает отзывы)"""
    courses = db.query(Review).offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=ReviewRead)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """Получить информацию о курсе по ID (временно возвращает отзыв)"""
    course = db.query(Review).filter(Review.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course


@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_course(review: ReviewCreate, db: Session = Depends(get_db)):
    """Создать курс (временно создает отзыв)"""
    db_review = Review(**review.model_dump())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.put("/{course_id}", response_model=ReviewRead)
async def update_course(course_id: int, review: ReviewCreate, db: Session = Depends(get_db)):
    """Обновить курс (временно обновляет отзыв)"""
    db_review = db.query(Review).filter(Review.id == course_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    for key, value in review.model_dump(exclude_unset=True).items():
        setattr(db_review, key, value)
    
    db.commit()
    db.refresh(db_review)
    return db_review


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Удалить курс (временно удаляет отзыв)"""
    db_review = db.query(Review).filter(Review.id == course_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    db.delete(db_review)
    db.commit()
    return None

