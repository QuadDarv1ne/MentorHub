"""
Middleware Registration Module

Centralized registration of all middleware for FastAPI application.
Order matters: middleware is executed in the order it's added.
"""

import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.config import is_production, settings
from app.constants import DEFAULT_MAX_BODY_SIZE
from app.middleware.rate_limiter_unified import UnifiedRateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.security_advanced import SecurityMiddleware
from app.utils.monitoring import PerformanceMiddleware, performance_monitor
from app.utils.prometheus import PrometheusMiddleware

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI, redis_client: Any = None) -> None:
    """
    Register all middleware for the application.

    Order is important:
    1. Request ID (must be first for tracing)
    2. Request Logging (after Request ID)
    3. Rate Limiting (early for protection)
    4. Prometheus Metrics
    5. Performance Monitoring
    6. Security (before CORS)
    7. CORS
    8. Trusted Host (production only)
    9. GZip Compression (last for response compression)

    Args:
        app: FastAPI application instance
        redis_client: Optional Redis client for rate limiting
    """

    # 1. Request ID Middleware (должен быть первым)
    app.add_middleware(RequestIDMiddleware)
    logger.info("✅ Request ID middleware added")

    # 2. Request Logging Middleware (сразу после Request ID)
    app.add_middleware(RequestLoggingMiddleware, max_body_length=1000)
    logger.info("✅ Request Logging middleware added")

    # 3. Rate Limiting Middleware (should be early in the chain)
    if settings.RATE_LIMIT_ENABLED:
        # Unified rate limiting (combines basic + advanced)
        app.add_middleware(
            UnifiedRateLimitMiddleware,
            redis_client=redis_client,
            enabled=True
        )
        logger.info("✅ Unified Rate limiting middleware added (per-endpoint limits)")
    else:
        logger.info("ℹ️ Rate limiting disabled by configuration")

    # 4. Prometheus Metrics Middleware
    app.add_middleware(PrometheusMiddleware)
    logger.info("✅ Prometheus metrics middleware added")

    # 5. Performance Monitoring Middleware
    app.add_middleware(PerformanceMiddleware, monitor=performance_monitor)
    logger.info("✅ Performance monitoring middleware added")

    # 6. Advanced Security Middleware (attack detection + security headers)
    app.add_middleware(
        SecurityMiddleware,
        max_body_size=DEFAULT_MAX_BODY_SIZE,
    )
    logger.info("✅ Advanced Security middleware added")

    # 7. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    logger.info("✅ CORS middleware added")

    # 8. Trusted Host Middleware (for production)
    if is_production():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )
        logger.info("✅ Trusted Host middleware added")

    # 9. GZIP Middleware for compression
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,
    )
    logger.info("✅ GZIP middleware added")
