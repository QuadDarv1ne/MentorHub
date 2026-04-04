"""
Course Lessons API
Управление уроками курсов
"""

import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, rate_limit_dependency
from app.models.course import Course, Lesson, CourseEnrollment
from app.models.progress import Progress
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


@router.post("/lessons/{lesson_id}/complete", status_code=status.HTTP_200_OK)
async def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Отметить урок как завершённый"""
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    # Проверяем что пользователь записан на курс
    enrollment = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.user_id == current_user.id,
            CourseEnrollment.course_id == lesson.course_id,
        )
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail="Вы не записаны на этот курс. Сначала запишитесь на курс."
        )

    # Создаём или обновляем запись прогресса для урока
    lesson_progress = (
        db.query(Progress)
        .filter(
            Progress.user_id == current_user.id,
            Progress.course_id == lesson.course_id,
            Progress.lesson_id == lesson_id,
        )
        .first()
    )

    if lesson_progress:
        # Обновляем существующую запись
        lesson_progress.completed = True
        lesson_progress.progress_percent = 100
    else:
        # Создаём новую запись
        lesson_progress = Progress(
            user_id=current_user.id,
            course_id=lesson.course_id,
            lesson_id=lesson_id,
            progress_percent=100,
            completed=True,
        )
        db.add(lesson_progress)

    # Считаем общее количество уроков в курсе
    total_lessons = (
        db.query(Lesson)
        .filter(Lesson.course_id == lesson.course_id)
        .count()
    )

    # Считаем количество завершённых уроков
    completed_lessons = (
        db.query(Progress)
        .filter(
            Progress.user_id == current_user.id,
            Progress.course_id == lesson.course_id,
            Progress.lesson_id.isnot(None),
            Progress.completed.is_(True),
        )
        .distinct(Progress.lesson_id)
        .count()
    )

    # Вычисляем общий прогресс курса
    if total_lessons > 0:
        course_progress = int((completed_lessons / total_lessons) * 100)
    else:
        course_progress = 0

    # Обновляем запись записи на курс
    enrollment.progress_percent = course_progress
    enrollment.completed = course_progress == 100

    if enrollment.completed and not enrollment.completed_at:
        from datetime import datetime
        enrollment.completed_at = datetime.utcnow()

    db.commit()

    # Инвалидируем кеш курса
    asyncio.create_task(invalidate_cache(f"course_detail:{lesson.course_id}"))

    return {
        "lesson_id": lesson.id,
        "lesson_title": lesson.title,
        "course_id": lesson.course_id,
        "course_progress": course_progress,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
        "course_completed": enrollment.completed,
    }
