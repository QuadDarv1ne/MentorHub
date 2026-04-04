"""
Application Lifespan Management

Startup and shutdown event handlers for FastAPI application.
Manages database connections, Redis, cache, and graceful shutdown.
"""

import logging
import asyncio
import signal
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import engine
from redis.asyncio import Redis

from app.config import settings, is_production
from app.database import Base
from app.utils.cache import init_cache
from app.utils.cache_advanced import init_cache_backend

logger = logging.getLogger(__name__)


# ==================== GRACEFUL SHUTDOWN ====================
# Глобальное событие для координации shutdown
_shutdown_event = asyncio.Event()
_shutdown_in_progress = False


def get_shutdown_event() -> asyncio.Event:
    """Get the global shutdown event for coordination"""
    return _shutdown_event


def is_shutdown_in_progress() -> bool:
    """Check if shutdown is in progress"""
    return _shutdown_in_progress


def signal_handler(signum, frame):
    """
    Обработчик сигналов для graceful shutdown.

    Вызывается при получении SIGTERM или SIGINT.
    Устанавливает флаг shutdown для graceful остановки.
    """
    global _shutdown_in_progress

    signal_name = signal.Signals(signum).name

    if _shutdown_in_progress:
        logger.warning(f"Received {signal_name} but shutdown already in progress, ignoring...")
        return

    _shutdown_in_progress = True
    logger.info(f"🛑 Received {signal_name}. Initiating graceful shutdown...")

    # Устанавливаем событие shutdown
    _shutdown_event.set()


# Регистрируем обработчики сигналов
# SIGTERM не поддерживается на Windows, используем SIGINT
import platform
if platform.system() != "Windows":
    signal.signal(signal.SIGTERM, signal_handler)
    logger.info("✅ Signal handlers registered for SIGTERM, SIGINT")
else:
    logger.info("✅ Signal handlers registered for SIGINT (Windows)")
signal.signal(signal.SIGINT, signal_handler)


# ==================== REDIS CLIENT SETUP ====================
redis_client: Optional[Redis] = None


def get_redis_client() -> Optional[Redis]:
    """Get the global Redis client"""
    return redis_client


def initialize_redis_client() -> Optional[Redis]:
    """Initialize Redis client if configured"""
    global redis_client
    
    try:
        from redis.asyncio import Redis
        
        # Initialize Redis if URL is configured (even localhost)
        if settings.REDIS_URL and settings.REDIS_URL.strip():
            redis_client = Redis.from_url(settings.REDIS_URL)
            logger.info(f"✅ Redis client initialized with URL: {settings.REDIS_URL[:50]}...")
        else:
            logger.info("ℹ️ Redis URL not configured, using memory-only features")
    except ImportError:
        logger.warning("⚠️ redis-py not installed, Redis features disabled")
    except Exception as e:
        logger.warning(f"⚠️ Redis client initialization failed: {e}")
        redis_client = None
    
    return redis_client


# ==================== SENTRY SETUP ====================
def initialize_sentry():
    """Initialize Sentry for production error tracking"""
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration

        SENTRY_AVAILABLE = True
    except ImportError:
        SENTRY_AVAILABLE = False

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
        logger.warning("⚠️ Sentry DSN configured, but sentry-sdk not installed")


# ==================== DATABASE STARTUP/SHUTDOWN ====================
async def startup_database():
    """Initialize database connection and create tables"""
    logger.info(f"📊 Database URL: {settings.DATABASE_URL[:50]}...")

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
                logger.error("❌ Failed to connect to database after all retries - starting anyway")
                # Don't crash on startup - database might not be ready yet
                pass


async def shutdown_database():
    """Close database connections gracefully"""
    logger.info("🔄 Closing database connections...")

    # Close any active sessions
    try:
        from app.database import SessionLocal
        SessionLocal.close_all()
        logger.info("✅ All database sessions closed")
    except Exception as e:
        logger.error(f"❌ Error closing database sessions: {e}")

    # Close database engine
    try:
        engine.dispose()
        logger.info("✅ Database engine disposed")
    except Exception as e:
        logger.error(f"❌ Error disposing database engine: {e}")


async def shutdown_redis():
    """Close Redis connection gracefully"""
    global redis_client
    
    if redis_client:
        try:
            await redis_client.aclose()
            logger.info("✅ Redis connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis connection: {e}")


# ==================== LIFESPAN CONTEXT MANAGER ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Manages database connections and other resources.

    IMPORTANT: Shutdown код выполняется при корректном завершении.
    При получении SIGTERM, Uvicorn вызывает этот shutdown код.
    """
    # ==================== STARTUP ====================
    logger.info("🚀 Starting MentorHub API...")

    # Initialize Sentry
    initialize_sentry()

    # Initialize Redis
    initialize_redis_client()

    # Initialize cache with Redis client if available
    init_cache(redis_client)
    init_cache_backend(redis_client)
    logger.info("✅ Cache initialized")

    # Initialize database
    await startup_database()

    # Log startup info
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔒 Debug mode: {settings.DEBUG}")
    logger.info(f"🌍 CORS origins: {settings.CORS_ORIGINS}")

    yield  # Application runs here

    # ==================== SHUTDOWN ====================
    logger.info("🛑 Lifespan shutdown triggered...")
    logger.info("🔄 Closing all connections gracefully...")

    # Close Redis connection
    await shutdown_redis()

    # Close database connections
    await shutdown_database()

    logger.info("✅ Lifespan shutdown complete")
