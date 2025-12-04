"""
Роуты курсов
API для работы с курсами
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.dependencies import get_db, rate_limit_dependency, get_current_user
from app.models.course import Course, Lesson, CourseEnrollment
from app.models.user import User
from app.models.mentor import Mentor
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, LessonCreate, LessonUpdate, LessonResponse, CourseEnrollmentCreate, CourseEnrollmentUpdate, CourseEnrollmentResponse, CourseWithLessonsResponse, CourseWithEnrollmentResponse
from app.utils.sanitization import sanitize_text_field, is_safe_string
from app.utils.cache import cached, invalidate_cache, CACHE_TTL

router = APIRouter()


@router.get("/", response_model=List[CourseResponse])
@cached(ttl=CACHE_TTL['course'], key_prefix="courses_list")
async def get_courses(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список курсов"""
    # Проверка на корректность параметров пагинации
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100

    courses = db.query(Course).offset(skip).limit(limit).all()
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
@cached(ttl=CACHE_TTL['course'], key_prefix="course_detail")
async def get_course(course_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить информацию о курсе по ID с уроками"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Get lessons for the course
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order).all()
    
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
    # Check if user is a mentor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=403, detail="Только менторы могут создавать курсы")
    
    # Санитизация входных данных
    sanitized_title = sanitize_text_field(course.title)
    sanitized_description = sanitize_text_field(course.description) if course.description else None
    sanitized_category = sanitize_text_field(course.category) if course.category else None
    
    # Проверка на безопасность входных данных
    if not is_safe_string(sanitized_title):
        raise HTTPException(status_code=400, detail="Недопустимые символы в названии курса")
    if sanitized_description and not is_safe_string(sanitized_description):
        raise HTTPException(status_code=400, detail="Недопустимые символы в описании курса")
    if sanitized_category and not is_safe_string(sanitized_category):
        raise HTTPException(status_code=400, detail="Недопустимые символы в категории курса")
    
    # Создаем курс с санитизированными данными
    db_course = Course(
        title=sanitized_title,
        description=sanitized_description,
        category=sanitized_category,
        difficulty=course.difficulty,
        duration_hours=course.duration_hours,
        price=course.price,
        is_active=course.is_active,
        thumbnail_url=course.thumbnail_url,
        instructor_id=mentor.id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
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
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Check if user is the course instructor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor or mentor.id != db_course.instructor_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь инструктором этого курса")
    
    # Санитизация входных данных
    sanitized_data = {}
    for key, value in course.model_dump(exclude_unset=True).items():
        if key in ["title", "description", "category"] and value is not None:
            sanitized_value = sanitize_text_field(value)
            if not is_safe_string(sanitized_value):
                field_name = "названии" if key == "title" else "описании" if key == "description" else "категории"
                raise HTTPException(status_code=400, detail=f"Недопустимые символы в {field_name} курса")
            sanitized_data[key] = sanitized_value
        else:
            sanitized_data[key] = value
    
    # Обновляем поля
    for key, value in sanitized_data.items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Удалить курс"""
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Check if user is the course instructor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor or mentor.id != db_course.instructor_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь инструктором этого курса")
    
    db.delete(db_course)
    db.commit()
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
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Check if user is the course instructor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor or mentor.id != course.instructor_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь инструктором этого курса")
    
    # Санитизация входных данных
    sanitized_title = sanitize_text_field(lesson.title)
    sanitized_description = sanitize_text_field(lesson.description) if lesson.description else None
    sanitized_content = sanitize_text_field(lesson.content) if lesson.content else None
    
    # Проверка на безопасность входных данных
    if not is_safe_string(sanitized_title):
        raise HTTPException(status_code=400, detail="Недопустимые символы в названии урока")
    if sanitized_description and not is_safe_string(sanitized_description):
        raise HTTPException(status_code=400, detail="Недопустимые символы в описании урока")
    if sanitized_content and not is_safe_string(sanitized_content):
        raise HTTPException(status_code=400, detail="Недопустимые символы в содержании урока")
    
    # Создаем урок с санитизированными данными
    db_lesson = Lesson(
        course_id=course_id,
        title=sanitized_title,
        description=sanitized_description,
        content=sanitized_content,
        video_url=lesson.video_url,
        duration_minutes=lesson.duration_minutes,
        order=lesson.order,
        is_preview=lesson.is_preview
    )
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
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
    
    # Check if user is the course instructor
    course = db.query(Course).filter(Course.id == db_lesson.course_id).first()
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor or mentor.id != course.instructor_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь инструктором этого курса")
    
    # Санитизация входных данных
    sanitized_data = {}
    for key, value in lesson.model_dump(exclude_unset=True).items():
        if key in ["title", "description", "content"] and value is not None:
            sanitized_value = sanitize_text_field(value)
            if not is_safe_string(sanitized_value):
                field_name = "названии" if key == "title" else "описании" if key == "description" else "содержании"
                raise HTTPException(status_code=400, detail=f"Недопустимые символы в {field_name} урока")
            sanitized_data[key] = sanitized_value
        else:
            sanitized_data[key] = value
    
    # Обновляем поля
    for key, value in sanitized_data.items():
        setattr(db_lesson, key, value)
    
    db.commit()
    db.refresh(db_lesson)
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
    
    # Check if user is the course instructor
    course = db.query(Course).filter(Course.id == db_lesson.course_id).first()
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor or mentor.id != course.instructor_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь инструктором этого курса")
    
    db.delete(db_lesson)
    db.commit()
    return None