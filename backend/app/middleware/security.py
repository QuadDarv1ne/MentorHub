"""
Security middleware для продакшена
Реализует дополнительные меры безопасности
"""

import logging
import time
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Добавляет заголовки безопасности"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security Headers
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.last_reset = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Сброс счетчиков каждую минуту
        current_time = time.time()
        if current_time - self.last_reset > 60:
            self.request_counts.clear()
            self.last_reset = current_time
        
        client_ip = get_remote_address(request)
        current_count = self.request_counts.get(client_ip, 0)
        
        # Проверка лимита
        if current_count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests"}
            )
        
        # Увеличение счетчика
        self.request_counts[client_ip] = current_count + 1
        
        response = await call_next(request)
        return response


class RequestSizeLimiterMiddleware(BaseHTTPMiddleware):
    """Ограничивает размер тела запроса"""
    
    def __init__(self, app, max_body_size: int = 10 * 1024 * 1024):  # 10MB по умолчанию
        super().__init__(app)
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Проверка размера тела запроса
        if request.method in ["POST", "PUT", "PATCH"]:
            # Получаем размер тела из заголовков
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_body_size:
                logger.warning(f"Request body too large: {content_length} bytes")
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Request body too large"}
                )
        
        response = await call_next(request)
        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Middleware для белого списка IP адресов (для админских эндпоинтов)"""
    
    def __init__(self, app, whitelisted_ips: list[str]):
        super().__init__(app)
        self.whitelisted_ips = set(whitelisted_ips)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Применяем только к определенным путям
        if request.url.path.startswith("/admin") or request.url.path.startswith("/internal"):
            client_ip = get_remote_address(request)
            
            if client_ip not in self.whitelisted_ips:
                logger.warning(f"Unauthorized access attempt from IP: {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Access denied"}
                )
        
        response = await call_next(request)
        return response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для аудита критических операций"""
    
    def __init__(self, app):
        super().__init__(app)
        self.audit_logger = logging.getLogger("audit")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Логируем критические операции
        audit_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/admin/",
            "/api/v1/payments/"
        ]
        
        should_audit = any(request.url.path.startswith(path) for path in audit_paths)
        
        if should_audit:
            user_id = getattr(request.state, "user_id", "anonymous")
            client_ip = get_remote_address(request)
            
            self.audit_logger.info(
                f"AUDIT: {request.method} {request.url.path} "
                f"User: {user_id} IP: {client_ip} "
                f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
            )
        
        response = await call_next(request)
        return response


# Rate limiter для использования с декораторами
limiter = Limiter(key_func=get_remote_address)

# Экспортируемые middleware
SECURITY_MIDDLEWARES = [
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestSizeLimiterMiddleware,
    AuditLoggingMiddleware
]