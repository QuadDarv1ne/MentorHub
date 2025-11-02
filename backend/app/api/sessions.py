"""
Роуты сессий
Заглушка для роутов, связанных с сессиями
TODO: Реализовать роуты сессий
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_sessions():
    """Получить список сессий"""
    return {"message": "Эндпоинт сессий - в разработке"}

