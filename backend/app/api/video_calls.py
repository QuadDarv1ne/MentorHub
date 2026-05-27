"""
Video Calls API Router
Объединяет все роуты для работы с видеозвонками
"""

from fastapi import APIRouter

from app.api.video_calls_agora import router as video_calls_agora_router
from app.api.video_calls_crud import router as video_calls_crud_router

# Создаем главный роутер
router = APIRouter()

# Включаем роуты
router.include_router(video_calls_crud_router)
router.include_router(video_calls_agora_router)
