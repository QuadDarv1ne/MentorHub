"""
Request Logging Middleware
Детальное логирование всех HTTP запросов
"""

import logging
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования HTTP запросов и ответов
    
    Логирует:
    - Метод и путь
    - Query параметры
    - Headers (без sensitive данных)
    - Body (для POST/PUT/PATCH)
    - Статус код ответа
    - Время обработки
    - IP адрес клиента
    - User Agent
    """
    
    def __init__(self, app: ASGIApp, max_body_length: int = 1000):
        super().__init__(app)
        self.max_body_length = max_body_length
        
        # Headers, которые не нужно логировать
        self.sensitive_headers = {
            'authorization',
            'cookie',
            'x-api-key',
            'x-csrf-token'
        }
        
        # Пути, которые не нужно логировать (чтобы не засорять логи)
        self.skip_paths = {
            '/health',
            '/metrics',
            '/docs',
            '/redoc',
            '/openapi.json',
            '/favicon.ico'
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Пропускаем технические endpoints
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # Получаем request ID из middleware
        request_id = request.state.request_id if hasattr(request.state, 'request_id') else 'N/A'

        # Засекаем время
        start_time = time.time()

        # Собираем информацию о запросе
        client_ip = request.client.host if request.client else 'unknown'
        method = request.method
        path = request.url.path

        # Headers (без sensitive данных)
        headers = {
            key: value for key, value in request.headers.items()
            if key.lower() not in self.sensitive_headers
        }
        
        user_agent = headers.get('user-agent', 'unknown')
        
        # Body для POST/PUT/PATCH
        body = None
        if method in ['POST', 'PUT', 'PATCH']:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body_str = body_bytes.decode('utf-8')
                    # Ограничиваем длину
                    if len(body_str) > self.max_body_length:
                        body_str = body_str[:self.max_body_length] + '...(truncated)'
                    
                    # Пытаемся распарсить JSON
                    try:
                        body = json.loads(body_str)
                        # Скрываем пароли
                        if isinstance(body, dict) and 'password' in body:
                            body['password'] = '***'
                    except json.JSONDecodeError:
                        body = body_str
            except Exception as e:
                logger.warning(f"Failed to read request body: {e}")
        
        # Логируем входящий запрос
        logger.info(
            f"🔵 [{request_id}] {method} {path} | "
            f"IP: {client_ip} | "
            f"User-Agent: {user_agent}"
        )

        # Обрабатываем запрос
        try:
            response = await call_next(request)
            
            # Время обработки
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)
            
            # Логируем ответ
            status_code = response.status_code
            
            # Выбираем уровень логирования в зависимости от статуса
            if status_code < 400:
                log_level = logging.INFO
                emoji = "✅"
            elif status_code < 500:
                log_level = logging.WARNING
                emoji = "⚠️"
            else:
                log_level = logging.ERROR
                emoji = "❌"
            
            logger.log(
                log_level,
                f"{emoji} [{request_id}] {status_code} {method} {path} | "
                f"Time: {process_time_ms}ms"
            )
            
            # Добавляем headers в ответ
            response.headers['X-Request-ID'] = request_id
            response.headers['X-Process-Time'] = str(process_time_ms)
            
            return response
            
        except Exception as e:
            # Логируем ошибку
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)
            
            logger.error(
                f"💥 [{request_id}] ERROR {method} {path} | "
                f"Time: {process_time_ms}ms | "
                f"Error: {str(e)}",
                exc_info=True
            )
            
            # Пробрасываем ошибку дальше
            raise


class SQLLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования SQL запросов (опционально)
    В production лучше использовать SQLAlchemy echo или отдельный logger
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Можно добавить логирование SQL через SQLAlchemy events
        # Или использовать SQLAlchemy echo=True в config
        
        response = await call_next(request)
        return response
