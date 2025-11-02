"""
Роуты платежей
Заглушка для роутов, связанных с платежами
TODO: Реализовать роуты платежей
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_payments():
    """Получить список платежей"""
    return {"message": "Эндпоинт платежей - в разработке"}

