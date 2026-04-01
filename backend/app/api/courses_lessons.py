"""
Course Lessons API
Управление уроками курсов
"""

import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, rate_limit_dependency
from app.models.course import Course, Lesson
from app.models.user import User
from app.schemas.course import LessonCreate, LessonUpdate, LessonResponse
from app.utils.cache import invalidate_cache

router = APIRouter()


@router.get("/{course_id}/lessons", response_model=List[LessonResponse])
async def get_course_lessons(
    course_id: int,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить список уроков курса"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    lessons = (
        db.query(Lesson)
        .filter(Lesson.course_id == course_id)
        .order_by(Lesson.order)
        .all()
    )

    return lessons


@router.post("/{course_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: int,
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Создать урок для курса"""
    # Проверяем существование курса
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Проверяем права (только инструктор курса может создавать уроки)
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    # Создаем урок
    db_lesson = Lesson(course_id=course_id, **lesson.model_dump())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)

    # Инвалидируем кеш курса
    asyncio.create_task(invalidate_cache(f"course_detail:{course_id}"))

    return db_lesson


@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить урок"""
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Проверяем права
    course = db.query(Course).filter(Course.id == db_lesson.course_id).first()
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    # Обновляем поля
    for key, value in lesson.model_dump(exclude_unset=True).items():
        setattr(db_lesson, key, value)

    db.commit()
    db.refresh(db_lesson)

    # Инвалидируем кеш курса
    asyncio.create_task(invalidate_cache(f"course_detail:{db_lesson.course_id}"))

    return db_lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Удалить урок"""
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Проверяем права
    course = db.query(Course).filter(Course.id == db_lesson.course_id).first()
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    course_id = db_lesson.course_id
    db.delete(db_lesson)
    db.commit()

    # Инвалидируем кеш курса
    asyncio.create_task(invalidate_cache(f"course_detail:{course_id}"))

    return None


@router.post("/lessons/{lesson_id}/complete", response_model=LessonResponse)
async def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Отметить урок как завершённый"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # TODO: Добавить логику отслеживания завершения урока для конкретного пользователя
    # Сейчас просто возвращаем урок

    return lesson
