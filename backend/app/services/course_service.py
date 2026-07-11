"""
Courses Service
Бизнес-логика для работы с курсами
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.course import Course, CourseEnrollment, Lesson
from app.models.mentor import Mentor
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate, LessonCreate, LessonUpdate
from app.utils.sanitization import sanitize_and_validate

logger = logging.getLogger(__name__)


class CourseService:
    """Сервис для управления курсами"""

    def __init__(self, db: Session):
        self.db = db

    def _sanitize_course_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Санитизация данных курса"""
        sanitized = {}
        for key, value in data.items():
            if key in ["title", "description", "category"] and value is not None:
                field_name = "названии" if key == "title" else "описании" if key == "description" else "категории"
                sanitized[key] = sanitize_and_validate(value, field_type="text", field_name=f"{field_name} курса")
            else:
                sanitized[key] = value
        return sanitized

    def _sanitize_lesson_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Санитизация данных урока"""
        sanitized = {}
        for key, value in data.items():
            if key in ["title", "description", "content"] and value is not None:
                field_name = "названии" if key == "title" else "описании" if key == "description" else "содержании"
                sanitized[key] = sanitize_and_validate(value, field_type="text", field_name=f"{field_name} урока")
            else:
                sanitized[key] = value
        return sanitized

    def check_mentor_access(self, user: User, course_instructor_id: int) -> bool:
        """Проверка прав ментора на курс"""
        mentor = self.db.query(Mentor).filter(Mentor.user_id == user.id).first()
        return mentor is not None and mentor.id == course_instructor_id

    def check_mentor_status(self, user: User) -> Optional[Mentor]:
        """Проверка статуса ментора"""
        return self.db.query(Mentor).filter(Mentor.user_id == user.id).first()

    def get_course_with_instructor(self, course_id: int) -> Optional[Course]:
        """Получить курс с данными инструктора"""
        return self.db.query(Course).options(
            joinedload(Course.instructor)
        ).filter(Course.id == course_id).first()

    def get_course_with_lessons(self, course_id: int) -> Optional[Course]:
        """Получить курс с уроками"""
        return self.db.query(Course).options(
            joinedload(Course.instructor),
            joinedload(Course.lessons)
        ).filter(Course.id == course_id).first()

    def get_user_enrollments(self, user_id: int) -> List[CourseEnrollment]:
        """Получить записи пользователя на курсы"""
        return self.db.query(CourseEnrollment).filter(
            CourseEnrollment.user_id == user_id
        ).all()

    def get_similar_courses(self, course: Course, limit: int = 5) -> List[Course]:
        """Получить похожие курсы"""
        return self.db.query(Course).filter(
            Course.id != course.id,
            Course.is_active.is_(True),
            or_(
                Course.category == course.category,
                Course.difficulty == course.difficulty,
            )
        ).limit(limit).all()

    def create_course(self, user: User, course_data: CourseCreate) -> Course:
        """Создать курс"""
        try:
            mentor = self.check_mentor_status(user)
            if not mentor:
                raise PermissionError("Только менторы могут создавать курсы")

            # Санитизация данных
            sanitized_data = self._sanitize_course_data(course_data.model_dump())

            db_course = Course(
                title=sanitized_data["title"],
                description=sanitized_data.get("description"),
                category=sanitized_data.get("category"),
                difficulty=course_data.difficulty,
                duration_hours=course_data.duration_hours,
                price=course_data.price,
                is_active=course_data.is_active,
                thumbnail_url=course_data.thumbnail_url,
                instructor_id=mentor.id
            )
            self.db.add(db_course)
            self.db.commit()
            self.db.refresh(db_course)
            return db_course
        except (PermissionError, ValueError):
            raise
        except Exception:
            logger.exception("Failed to create course by user %s", user.id)
            self.db.rollback()
            raise

    def update_course(self, course_id: int, user: User, course_data: CourseUpdate) -> Course:
        """Обновить курс"""
        try:
            db_course = self.get_course_with_instructor(course_id)
            if not db_course:
                raise ValueError("Курс не найден")

            if not self.check_mentor_access(user, db_course.instructor_id):
                raise PermissionError("Вы не являетесь инструктором этого курса")

            # Санитизация и обновление
            sanitized_data = self._sanitize_course_data(course_data.model_dump(exclude_unset=True))
            for key, value in sanitized_data.items():
                setattr(db_course, key, value)

            self.db.commit()
            self.db.refresh(db_course)
            return db_course
        except (PermissionError, ValueError):
            raise
        except Exception:
            logger.exception("Failed to update course %s by user %s", course_id, user.id)
            self.db.rollback()
            raise

    def create_lesson(self, course_id: int, user: User, lesson_data: LessonCreate) -> Lesson:
        """Создать урок"""
        try:
            course = self.get_course_with_instructor(course_id)
            if not course:
                raise ValueError("Курс не найден")

            if not self.check_mentor_access(user, course.instructor_id):
                raise PermissionError("Вы не являетесь инструктором этого курса")

            # Санитизация данных
            sanitized_data = self._sanitize_lesson_data(lesson_data.model_dump())

            db_lesson = Lesson(
                course_id=course_id,
                title=sanitized_data["title"],
                description=sanitized_data.get("description"),
                content=sanitized_data.get("content"),
                video_url=lesson_data.video_url,
                duration_minutes=lesson_data.duration_minutes,
                order=lesson_data.order,
                is_preview=lesson_data.is_preview
            )
            self.db.add(db_lesson)
            self.db.commit()
            self.db.refresh(db_lesson)
            return db_lesson
        except (PermissionError, ValueError):
            raise
        except Exception:
            logger.exception("Failed to create lesson in course %s by user %s", course_id, user.id)
            self.db.rollback()
            raise

    def update_lesson(self, lesson_id: int, user: User, lesson_data: LessonUpdate) -> Lesson:
        """Обновить урок"""
        try:
            db_lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if not db_lesson:
                raise ValueError("Урок не найден")

            course = self.get_course_with_instructor(db_lesson.course_id)
            if not self.check_mentor_access(user, course.instructor_id if course else -1):
                raise PermissionError("Вы не являетесь инструктором этого курса")

            # Санитизация и обновление
            sanitized_data = self._sanitize_lesson_data(lesson_data.model_dump(exclude_unset=True))
            for key, value in sanitized_data.items():
                setattr(db_lesson, key, value)

            self.db.commit()
            self.db.refresh(db_lesson)
            return db_lesson
        except (PermissionError, ValueError):
            raise
        except Exception:
            logger.exception("Failed to update lesson %s by user %s", lesson_id, user.id)
            self.db.rollback()
            raise


# Глобальная функция для инвалидации кеша (используется в API)
async def invalidate_course_cache(db: Session, course_id: int):
    """Инвалидация кеша курса"""
    import asyncio

    from app.utils.cache import invalidate_cache

    asyncio.create_task(invalidate_cache(f"course_detail:{course_id}"))
    asyncio.create_task(invalidate_cache("courses_list:*"))
