"""
Courses CRUD Operations
Базовые CRUD операции для курсов
"""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db, rate_limit_dependency
from app.models.course import Course
from app.models.user import User, UserRole
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate, CourseWithLessonsResponse

logger = logging.getLogger(__name__)
from app.services.cache import cached
from app.services.course_service import CourseService
from app.utils.cache import invalidate_cache

router = APIRouter()


async def _safe_invalidate_cache(key: str):
    """Fire-and-forget cache invalidation with error logging."""
    try:
        await invalidate_cache(key)
    except Exception:
        logger.exception("Failed to invalidate cache: %s", key)


def _get_course_service(db: Session) -> CourseService:
    """Получить сервис курсов"""
    return CourseService(db)


@router.get("/", response_model=list[CourseResponse])
@cached(ttl=1800, key_prefix="courses_list")
async def get_courses(
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить список курсов с фильтрацией"""
    from app.utils.pagination import validate_pagination
    skip, limit = validate_pagination(skip, limit)

    query = db.query(Course).options(joinedload(Course.instructor))

    if category:
        query = query.filter(Course.category == category)

    return query.offset(skip).limit(limit).all()


@router.get("/{course_id}", response_model=CourseWithLessonsResponse)
@cached(ttl=1800, key_prefix="course_detail")
async def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить информацию о курсе по ID с уроками"""
    course = (
        db.query(Course)
        .options(
            joinedload(Course.instructor),
            joinedload(Course.lessons)
        )
        .filter(Course.id == course_id)
        .first()
    )

    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Создать новый курс"""
    service = _get_course_service(db)
    new_course = service.create_course(current_user, course)

    # Инвалидируем кеш списка курсов
    asyncio.create_task(_safe_invalidate_cache("courses_list:"))

    return new_course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить курс"""
    service = _get_course_service(db)
    updated_course = service.update_course(course_id, current_user, course)

    # Инвалидируем кеш
    asyncio.create_task(_safe_invalidate_cache(f"course_detail:{course_id}"))
    asyncio.create_task(_safe_invalidate_cache("courses_list:"))

    return updated_course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Удалить курс"""
    # Проверяем существование курса
    existing_course = db.query(Course).filter(Course.id == course_id).first()
    if not existing_course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Проверяем права (ментор или админ)
    from app.models.mentor import Mentor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    is_instructor = mentor and existing_course.instructor_id == mentor.id
    is_admin = current_user.role == UserRole.ADMIN

    if not is_instructor and not is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    try:
        db.delete(existing_course)
        db.commit()

        # Инвалидируем кеш
        asyncio.create_task(_safe_invalidate_cache(f"course_detail:{course_id}"))
        asyncio.create_task(_safe_invalidate_cache("courses_list:"))

        return None
    except Exception:
        logger.exception("Failed to delete course %s by user %s", course_id, current_user.id)
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при удалении курса")


@router.get("/{course_id}/similar", response_model=list[dict])
async def get_similar_courses(
    course_id: int,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить похожие курсы"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Поиск похожих курсов по категории
    similar = (
        db.query(Course)
        .filter(
            Course.category == course.category,
            Course.id != course_id,
            Course.is_active.is_(True)
        )
        .limit(5)
        .all()
    )

    return [
        {
            "id": c.id,
            "title": c.title,
            "category": c.category,
            "instructor_id": c.instructor_id,
        }
        for c in similar
    ]
