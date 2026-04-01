"""
Courses API Router
Объединяет все роуты для работы с курсами
"""

from fastapi import APIRouter

from app.api.courses_crud import router as courses_crud_router
from app.api.courses_lessons import router as courses_lessons_router
from app.api.courses_enrollments import router as courses_enrollments_router

# Создаем главный роутер
router = APIRouter()

# Включаем роуты
router.include_router(courses_crud_router)
router.include_router(courses_lessons_router)
router.include_router(courses_enrollments_router)
