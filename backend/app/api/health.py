"""
Health Check Endpoints для мониторинга состояния приложения
"""

import logging
import psutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.utils.cache import cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """
    Базовая проверка работоспособности API

    Returns:
        dict: Статус сервиса
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "mentorhub-api",
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Детальная проверка работоспособности всех компонентов

    Returns:
        dict: Детальная информация о состоянии компонентов

    Raises:
        HTTPException: Если какой-то компонент недоступен
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {},
    }

    # Проверка БД
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": str(e),
        }
        health_status["status"] = "degraded"

    # Проверка Redis Cache
    try:
        test_key = "__health_check__"
        cache_manager.set(test_key, "ok", ttl=10)
        result = cache_manager.get(test_key)
        if result == "ok":
            health_status["components"]["cache"] = {
                "status": "healthy",
                "message": "Redis cache operational",
            }
        else:
            health_status["components"]["cache"] = {
                "status": "unhealthy",
                "message": "Cache read/write mismatch",
            }
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        health_status["components"]["cache"] = {
            "status": "unhealthy",
            "message": str(e),
        }
        health_status["status"] = "degraded"

    # Системные метрики
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        health_status["components"]["system"] = {
            "status": "healthy",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
        }

        # Предупреждение о высокой нагрузке
        if cpu_percent > 80 or memory.percent > 90 or disk.percent > 90:
            health_status["status"] = "degraded"
            health_status["components"]["system"]["warning"] = (
                "High resource usage detected"
            )

    except Exception as e:
        logger.error(f"System metrics health check failed: {e}")
        health_status["components"]["system"] = {
            "status": "unknown",
            "message": str(e),
        }

    # Если статус degraded или unhealthy, возвращаем 503
    if health_status["status"] != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status,
        )

    return health_status


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe - проверка готовности принимать трафик

    Returns:
        dict: Статус готовности

    Raises:
        HTTPException: Если сервис не готов
    """
    try:
        # Проверяем подключение к БД
        db.execute(text("SELECT 1"))

        # Проверяем кэш
        cache_manager.get("__readiness_check__")

        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "error": str(e)},
        )


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe - проверка что приложение живо

    Returns:
        dict: Статус liveness
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
