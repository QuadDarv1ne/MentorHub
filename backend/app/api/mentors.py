"""
Роуты менторов
Заглушка для роутов, связанных с менторами
TODO: Реализовать роуты менторов
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_mentors():
    """Получить список менторов"""
    return {"message": "Эндпоинт менторов - в разработке"}

