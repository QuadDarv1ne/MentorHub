"""
Роуты сообщений
Заглушка для роутов, связанных с сообщениями/чатом
TODO: Реализовать роуты сообщений
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_messages():
    """Получить список сообщений"""
    return {"message": "Эндпоинт сообщений - в разработке"}

