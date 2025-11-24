"""
Request ID Middleware для отслеживания запросов
"""

import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware для добавления уникального ID к каждому запросу
    Помогает отслеживать запросы в логах и debugging
    """

    async def dispatch(self, request: Request, call_next):
        # Получаем request ID из заголовков или генерируем новый
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Добавляем request_id в state запроса для доступа в эндпоинтах
        request.state.request_id = request_id

        # Обрабатываем запрос
        response = await call_next(request)

        # Добавляем request_id в заголовки ответа
        response.headers["X-Request-ID"] = request_id

        return response


def get_request_id(request: Request) -> str:
    """
    Получение request_id из текущего запроса

    Args:
        request: FastAPI Request object

    Returns:
        Request ID string
    """
    return getattr(request.state, "request_id", "unknown")
