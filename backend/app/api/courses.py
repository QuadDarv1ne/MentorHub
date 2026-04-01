"""
Роуты курсов
API для работы с курсами
"""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, rate_limit_dependency, get_current_user
from app.models.course import Course, Lesson, CourseEnrollment
from app.models.user import User
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse,
    LessonCreate, LessonUpdate, LessonResponse,
    CourseEnrollmentCreate, CourseEnrollmentUpdate, CourseEnrollmentResponse,
    CourseWithLessonsResponse, CourseWithEnrollmentResponse
)
from app.services.cache import cached
from app.services.course_service import CourseService, invalidate_course_cache

router = APIRouter()


def _get_course_service(db: Session) -> CourseService:
    """Получить сервис курсов"""
    return CourseService(db)


@router.get("/", response_model=List[CourseResponse])
@cached(ttl=1800, key_prefix="courses_list")
async def get_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список курсов"""
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100

    service = _get_course_service(db)
    courses = db.query(Course).options(
        joinedload(Course.instructor)
    ).offset(skip).limit(limit).all()
    return courses


@router.get("/my", response_model=List[CourseWithEnrollmentResponse])
async def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить список курсов текущего пользователя с информацией о записи"""
    # Get user's course enrollments
    enrollments = db.query(CourseEnrollment).filter(CourseEnrollment.user_id == current_user.id).all()
    course_ids = [enrollment.course_id for enrollment in enrollments]
    
    if not course_ids:
        return []
    
    # Get courses with enrollments
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
    
    # Create response with enrollment info
    result = []
    enrollment_map = {enrollment.course_id: enrollment for enrollment in enrollments}
    
    for course in courses:
        course_with_enrollment = CourseWithEnrollmentResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            category=course.category,
            difficulty=course.difficulty,
            duration_hours=course.duration_hours,
            price=course.price,
            is_active=course.is_active,
            rating=course.rating,
            total_reviews=course.total_reviews,
            thumbnail_url=course.thumbnail_url,
            instructor_id=course.instructor_id,
            created_at=course.created_at,
            updated_at=course.updated_at,
            enrollment=enrollment_map.get(course.id)
        )
        result.append(course_with_enrollment)
    
    return result


@router.get("/{course_id}", response_model=CourseWithLessonsResponse)
@cached(ttl=1800, key_prefix="course_detail")
async def get_course(course_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить информацию о курсе по ID с уроками"""
    # Используем joinedload для загрузки instructor и lessons вместе с курсом (избегаем N+1)
    course = db.query(Course).options(
        joinedload(Course.instructor),
        joinedload(Course.lessons)
    ).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Lessons уже загружены через joinedload, сортируем их
    lessons = sorted(course.lessons, key=lambda x: x.order)
    
    course_with_lessons = CourseWithLessonsResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        category=course.category,
        difficulty=course.difficulty,
        duration_hours=course.duration_hours,
        price=course.price,
        is_active=course.is_active,
        rating=course.rating,
        total_reviews=course.total_reviews,
        thumbnail_url=course.thumbnail_url,
        instructor_id=course.instructor_id,
        created_at=course.created_at,
        updated_at=course.updated_at,
        lessons=lessons
    )
    
    return course_with_lessons


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Создать курс"""
    service = _get_course_service(db)
    
    try:
        db_course = service.create_course(current_user, course)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return db_course


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
    
    try:
        db_course = service.update_course(course_id, current_user, course)
        # Инвалидируем кеш
        await invalidate_course_cache(db, course_id)
        return db_course
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Удалить курс"""
    service = _get_course_service(db)
    
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    if not service.check_mentor_access(current_user, db_course.instructor_id):
        raise HTTPException(status_code=403, detail="Вы не являетесь инструктором этого курса")

    db.delete(db_course)
    db.commit()

    # Инвалидируем кеш
    await invalidate_course_cache(db, course_id)

    return None


@router.post("/{course_id}/enroll", response_model=CourseEnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Записаться на курс"""
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Check if already enrolled
    existing_enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == current_user.id,
        CourseEnrollment.course_id == course_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Вы уже записаны на этот курс")
    
    # Create enrollment
    enrollment = CourseEnrollment(
        user_id=current_user.id,
        course_id=course_id,
        progress_percent=0,
        completed=False
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/{course_id}/lessons", response_model=List[LessonResponse])
async def get_course_lessons(
    course_id: int, 
    db: Session = Depends(get_db), 
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить уроки курса"""
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order).all()
    return lessons


@router.post("/{course_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: int,
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Создать урок в курсе"""
    service = _get_course_service(db)
    
    try:
        db_lesson = service.create_lesson(course_id, current_user, lesson)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
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
    service = _get_course_service(db)
    
    try:
        db_lesson = service.update_lesson(lesson_id, current_user, lesson)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return db_lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Удалить урок"""
    service = _get_course_service(db)
    
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    course = db.query(Course).filter(Course.id == db_lesson.course_id).first()
    if not service.check_mentor_access(current_user, course.instructor_id if course else -1):
        raise HTTPException(status_code=403, detail="Вы не являетесь инструктором этого курса")

    db.delete(db_lesson)
    db.commit()
    return None


@router.get("/{course_id}/similar", response_model=List[dict])
async def get_similar_courses(
    course_id: int,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить похожие курсы на основе категории"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")

    # Найти курсы с той же категорией
    similar = (
        db.query(Course)
        .filter(
            Course.id != course_id,
            Course.is_active == True,
            or_(
                Course.category == course.category,
                Course.difficulty == course.difficulty,
            )
        )
        .limit(5)
        .all()
    )

    # Вернуть упрощённые данные
    result = []
    for c in similar:
        result.append({
            "course_id": c.id,
            "average_rating": c.rating,
            "total_reviews": c.total_reviews,
        })

    return result