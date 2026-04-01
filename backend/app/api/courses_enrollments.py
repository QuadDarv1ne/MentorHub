"""
Course Enrollments API
Управление записями на курсы
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, get_current_user, rate_limit_dependency
from app.models.course import Course, CourseEnrollment
from app.models.user import User
from app.schemas.course import CourseEnrollmentResponse, CourseWithEnrollmentResponse
from app.services.course_service import CourseService

router = APIRouter()


def _get_course_service(db: Session) -> CourseService:
    """Получить сервис курсов"""
    return CourseService(db)


@router.get("/my", response_model=List[CourseWithEnrollmentResponse])
async def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить курсы текущего пользователя"""
    enrollments = (
        db.query(CourseEnrollment)
        .options(
            joinedload(CourseEnrollment.course).joinedload(Course.instructor),
            joinedload(CourseEnrollment.course).joinedload(Course.lessons)
        )
        .filter(CourseEnrollment.user_id == current_user.id)
        .all()
    )

    result = []
    for enrollment in enrollments:
        course_dict = {
            "id": enrollment.course.id,
            "title": enrollment.course.title,
            "description": enrollment.course.description,
            "category": enrollment.course.category,
            "difficulty_level": enrollment.course.difficulty_level,
            "duration_hours": enrollment.course.duration_hours,
            "instructor_id": enrollment.course.instructor_id,
            "is_active": enrollment.course.is_active,
            "created_at": enrollment.course.created_at,
            "updated_at": enrollment.course.updated_at,
            "instructor": enrollment.course.instructor,
            "lessons": enrollment.course.lessons,
            "enrollment": {
                "id": enrollment.id,
                "enrolled_at": enrollment.enrolled_at,
                "completed": enrollment.completed,
                "progress": enrollment.progress,
            }
        }
        result.append(course_dict)

    return result


@router.post("/{course_id}/enroll", response_model=CourseEnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Записаться на курс"""
    # Проверяем существование курса
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Проверяем, не записан ли уже пользователь
    existing = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == current_user.id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Вы уже записаны на этот курс"
        )

    # Создаем запись
    enrollment = CourseEnrollment(
        user_id=current_user.id,
        course_id=course_id,
        progress=0,
        completed=False
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment


@router.delete("/{course_id}/enroll", status_code=status.HTTP_204_NO_CONTENT)
async def unenroll_from_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Отписаться от курса"""
    enrollment = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == current_user.id
        )
        .first()
    )

    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Вы не записаны на этот курс"
        )

    db.delete(enrollment)
    db.commit()

    return None


@router.put("/{course_id}/progress", response_model=CourseEnrollmentResponse)
async def update_course_progress(
    course_id: int,
    progress: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить прогресс прохождения курса"""
    if progress < 0 or progress > 100:
        raise HTTPException(
            status_code=400,
            detail="Прогресс должен быть от 0 до 100"
        )

    enrollment = (
        db.query(CourseEnrollment)
        .filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == current_user.id
        )
        .first()
    )

    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Вы не записаны на этот курс"
        )

    enrollment.progress = progress
    enrollment.completed = (progress == 100)

    db.commit()
    db.refresh(enrollment)

    return enrollment
