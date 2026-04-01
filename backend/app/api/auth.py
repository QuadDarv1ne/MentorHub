"""
Authentication API Router
Объединяет core auth и OAuth роуты
"""

from fastapi import APIRouter

from app.api.auth_core import router as auth_core_router
from app.api.auth_oauth import router as auth_oauth_router

# Создаем главный роутер
router = APIRouter()

# Включаем роуты
router.include_router(auth_core_router)
router.include_router(auth_oauth_router)
