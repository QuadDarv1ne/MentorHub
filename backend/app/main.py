"""
MentorHub Backend - Main Entry Point
FastAPI application initialization and configuration
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from app.config import settings, is_production
from app.database import engine, Base, SessionLocal
from app.api import (
    auth,
    users,
    mentors,
    sessions,
    messages,
    payments,
    courses,
    reviews,
    progress,
    stats,
    monitoring,
    health,
    achievements,
    backups,
    email_verification,
    websocket,
    notifications,
)
from app.middleware.security_advanced import SecurityMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.utils.monitoring import PerformanceMiddleware, performance_monitor
from app.utils.prometheus import PrometheusMiddleware, metrics_endpoint
from app.utils.cache import init_cache
from app.utils.error_handlers import register_error_handlers


# ==================== LOGGING SETUP ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ==================== SENTRY SETUP ====================
if SENTRY_AVAILABLE and settings.SENTRY_DSN and is_production():
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )
    logger.info("✅ Sentry initialized")
elif settings.SENTRY_DSN and not SENTRY_AVAILABLE:
    logger.warning("⚠️ Sentry DSN настроен, но sentry-sdk не установлен")

# ==================== REDIS CLIENT SETUP ====================
redis_client = None
try:
    from redis.asyncio import Redis
    # Initialize Redis if URL is configured (even localhost)
    if settings.REDIS_URL and settings.REDIS_URL.strip():
        redis_client = Redis.from_url(settings.REDIS_URL)
        logger.info(f"✅ Redis client initialized with URL: {settings.REDIS_URL}")
    else:
        logger.info("ℹ️ Redis URL not configured, using memory-only features")
except ImportError:
    logger.warning("⚠️ redis-py not installed, Redis features disabled")
except Exception as e:
    logger.warning(f"⚠️ Redis client initialization failed: {e}")
    redis_client = None

# ==================== DATABASE STARTUP/SHUTDOWN ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    Manages database connections and other resources
    """
    # STARTUP
    logger.info("🚀 Starting MentorHub API...")
    logger.info(f"📊 Database URL: {settings.DATABASE_URL[:50]}...")

    # Initialize cache with Redis client if available
    init_cache(redis_client)
    logger.info("✅ Cache initialized")

    # Create tables (with retry logic for Amvera)
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            import time

            if attempt > 0:
                logger.info(f"⏳ Retrying database connection (attempt {attempt + 1}/{max_retries})...")
                time.sleep(retry_delay)

            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created/verified")
            break
        except Exception as e:
            logger.error(f"❌ Error creating database tables (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logger.error("❌ Failed to connect to database after all retries")
                # Don't raise in production, let app start anyway
                if not is_production():
                    raise

    # Log startup info
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔒 Debug mode: {settings.DEBUG}")
    logger.info(f"🌍 CORS origins: {settings.CORS_ORIGINS}")

    yield  # Application runs here

    # SHUTDOWN
    # Close Redis connection if it exists
    if redis_client:
        try:
            # Create a task to close the Redis connection
            import asyncio
            async def close_redis():
                await redis_client.close()
            
            # Run in a new event loop if needed
            try:
                loop = asyncio.get_running_loop()
                # If we're in an event loop, create a task
                loop.create_task(close_redis())
            except RuntimeError:
                # No event loop running, create a new one
                close_loop = asyncio.new_event_loop()
                close_loop.run_until_complete(close_redis())
                close_loop.close()
            
            logger.info("✅ Redis connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis connection: {e}")
    
    logger.info("🛑 Shutting down MentorHub API...")
    logger.info("✅ MentorHub API shutdown complete")


# ==================== CREATE FASTAPI APP ====================
app = FastAPI(
    title=settings.APP_NAME,
    description="Open-source IT mentorship platform API",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if not is_production() else None,
    redoc_url="/redoc" if not is_production() else None,
    openapi_url="/openapi.json" if not is_production() else None,
)


# ==================== MIDDLEWARE SETUP ====================

# Request ID Middleware (должен быть первым)
app.add_middleware(RequestIDMiddleware)
logger.info("✅ Request ID middleware added")

# Request Logging Middleware (сразу после Request ID)
app.add_middleware(RequestLoggingMiddleware, max_body_length=1000)
logger.info("✅ Request Logging middleware added")

# Rate Limiting Middleware (should be early in the chain)
# Always add rate limiting middleware, even without Redis it will use memory fallback
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        redis_client=redis_client  # Will use memory fallback if None
    )
    logger.info("✅ Rate limiting middleware added")
else:
    logger.info("ℹ️ Rate limiting disabled by configuration")

# Prometheus Metrics Middleware
app.add_middleware(PrometheusMiddleware)
logger.info("✅ Prometheus metrics middleware added")

# Performance Monitoring Middleware
app.add_middleware(PerformanceMiddleware, monitor=performance_monitor)
logger.info("✅ Performance monitoring middleware added")

# Advanced Security Middleware (SQL injection, XSS, CSRF, etc.)
app.add_middleware(
    SecurityMiddleware,
    max_body_size=10 * 1024 * 1024,  # 10MB
)
logger.info("✅ Advanced Security middleware added")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)
logger.info("✅ CORS middleware added")

# Trusted Host Middleware (for production)
if is_production():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    logger.info("✅ Trusted Host middleware added")

# GZIP Middleware for compression
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)
logger.info("✅ GZIP middleware added")


# ==================== EXCEPTION HANDLERS ====================

# Регистрируем централизованные обработчики ошибок
register_error_handlers(app)


# ==================== REQUEST/RESPONSE LOGGING ====================


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses"""

    # Skip logging for health checks and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    logger.info(f"📨 {request.method} {request.url.path}")

    response = await call_next(request)

    logger.info(f"📤 {response.status_code} {request.method} {request.url.path}")

    return response


# ==================== ROUTES SETUP ====================


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not is_production() else None,
    }


# Prometheus metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Prometheus metrics endpoint"""
    return await metrics_endpoint()


# ==================== API ROUTES ====================
api_prefix = "/api/v1"

# Health routes
app.include_router(
    health.router,
    prefix=api_prefix,
)

# Auth routes
app.include_router(
    auth.router,
    prefix=f"{api_prefix}/auth",
    tags=["Authentication"],
)
logger.info("✅ Auth routes loaded")

# Email verification routes
app.include_router(
    email_verification.router,
    prefix=f"{api_prefix}/email",
    tags=["Email Verification"],
)
logger.info("✅ Email verification routes loaded")

# User routes
app.include_router(
    users.router,
    prefix=f"{api_prefix}/users",
    tags=["Users"],
)
logger.info("✅ User routes loaded")

# Mentor routes
app.include_router(
    mentors.router,
    prefix=f"{api_prefix}/mentors",
    tags=["Mentors"],
)
logger.info("✅ Mentor routes loaded")

# Session routes
app.include_router(
    sessions.router,
    prefix=f"{api_prefix}/sessions",
    tags=["Sessions"],
)
logger.info("✅ Session routes loaded")

# Message routes
app.include_router(
    messages.router,
    prefix=f"{api_prefix}/messages",
    tags=["Messages"],
)
logger.info("✅ Message routes loaded")

# Payment routes
app.include_router(
    payments.router,
    prefix=f"{api_prefix}/payments",
    tags=["Payments"],
)
logger.info("✅ Payment routes loaded")

# Course routes
app.include_router(
    courses.router,
    prefix=f"{api_prefix}/courses",
    tags=["Courses"],
)
logger.info("✅ Course routes loaded")

# Review routes
app.include_router(
    reviews.router,
    prefix=f"{api_prefix}",
    tags=["Reviews"],
)
logger.info("✅ Review routes loaded")


app.include_router(
    progress.router,
    prefix=f"{api_prefix}",
    tags=["Progress"],
)
logger.info("✅ Progress routes loaded")

# Stats routes
app.include_router(
    stats.router,
    prefix=f"{api_prefix}",
    tags=["Statistics"],
)
logger.info("✅ Stats routes loaded")

# Achievement routes
app.include_router(
    achievements.router,
    prefix=f"{api_prefix}/achievements",
    tags=["Achievements"],
)
logger.info("✅ Achievement routes loaded")

# Monitoring routes
app.include_router(
    monitoring.router,
    prefix=f"{api_prefix}/admin",
    tags=["Monitoring"],
)
logger.info("✅ Monitoring routes loaded")

# Backup routes
app.include_router(
    backups.router,
    prefix=f"{api_prefix}/admin",
    tags=["Backups"],
)
logger.info("✅ Backup routes loaded")

# WebSocket routes
app.include_router(
    websocket.router,
    tags=["WebSocket"],
)
logger.info("✅ WebSocket routes loaded")

# Notification routes
app.include_router(
    notifications.router,
    prefix=f"{api_prefix}",
    tags=["Notifications"],
)
logger.info("✅ Notification routes loaded")


# ==================== STARTUP EVENTS ====================

# Note: Using lifespan context manager instead of deprecated @app.on_event
# Startup/shutdown logic is handled in the lifespan() function above


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app=app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )
