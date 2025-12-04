"""
Security Headers Middleware
Добавление заголовков безопасности для защиты от различных атак
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware для добавления заголовков безопасности

    Защита от:
    - XSS атак
    - Clickjacking
    - MIME-type sniffing
    - Information disclosure
    """

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # Prevent XSS attacks
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy - Улучшенная версия
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "img-src 'self' data: https: blob:",
            "font-src 'self' data: https://fonts.gstatic.com",
            "connect-src 'self' https://api.github.com https://accounts.google.com",
            "media-src 'self' https:",
            "object-src 'none'",
            "frame-src 'none'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "upgrade-insecure-requests",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # HSTS - Force HTTPS (only in production)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature Policy)
        permissions = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)

        # Remove server header
        response.headers["Server"] = "MentorHub"

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования входящих запросов
    """

    async def dispatch(self, request: Request, call_next: Callable):
        import time
        import logging

        logger = logging.getLogger("api")

        # Start timer
        start_time = time.time()

        # Get client info
        client_ip = request.headers.get("X-Forwarded-For", request.client.host)

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log request
        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration:.3f}s "
            f"client={client_ip}"
        )

        # Add custom headers
        response.headers["X-Process-Time"] = f"{duration:.3f}"

        return response
