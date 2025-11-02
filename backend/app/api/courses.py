"""
Роуты курсов
Заглушка для роутов, связанных с курсами
TODO: Реализовать роуты курсов
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_courses():
    """Получить список курсов"""
    return {"message": "Эндпоинт курсов - в разработке"}

