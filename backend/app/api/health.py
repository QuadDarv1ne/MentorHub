"""
Health check endpoint для мониторинга состояния приложения
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import redis
import psutil
import time

from app.database import get_db
from app.dependencies import get_redis
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])

def get_system_metrics() -> Dict[str, Any]:
    """Получает системные метрики"""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "uptime_seconds": time.time() - psutil.boot_time()
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {}

@router.get("")
async def health_check(
    db = Depends(get_db),
    redis_client = Depends(get_redis)
) -> JSONResponse:
    """
    Базовая проверка здоровья приложения
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {}
    }
    
    # Проверка базы данных
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Проверка Redis
    try:
        redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except (redis.ConnectionError, redis.TimeoutError) as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    return JSONResponse(
        status_code=status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=health_status
    )

@router.get("/detailed")
async def detailed_health_check(
    db = Depends(get_db),
    redis_client = Depends(get_redis)
) -> JSONResponse:
    """
    Детальная проверка здоровья с расширенной информацией
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "services": {},
        "system": get_system_metrics()
    }
    
    # Проверка базы данных с детальной информацией
    try:
        # Базовая проверка
        result = db.execute(text("SELECT 1")).fetchone()
        
        # Получение информации о соединениях
        connections_info = db.execute(text("""
            SELECT count(*) as active_connections 
            FROM pg_stat_activity 
            WHERE datname = current_database()
        """)).fetchone()
        
        health_status["services"]["database"] = {
            "status": "healthy",
            "active_connections": connections_info[0] if connections_info else 0,
            "response_time_ms": 0  # Можно добавить измерение времени
        }
    except SQLAlchemyError as e:
        logger.error(f"Detailed database health check failed: {e}")
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Проверка Redis с детальной информацией
    try:
        start_time = time.time()
        redis_client.ping()
        response_time = (time.time() - start_time) * 1000
        
        # Получение информации о Redis
        info = redis_client.info()
        
        health_status["services"]["redis"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "used_memory_mb": round(info.get("used_memory_rss", 0) / 1024 / 1024, 2),
            "connected_clients": info.get("connected_clients", 0),
            "uptime_seconds": info.get("uptime_in_seconds", 0)
        }
    except (redis.ConnectionError, redis.TimeoutError) as e:
        logger.error(f"Detailed Redis health check failed: {e}")
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Проверка внешних сервисов (если есть)
    external_services = []
    if hasattr(settings, 'EXTERNAL_SERVICES'):
        external_services = settings.EXTERNAL_SERVICES
    
    for service in external_services:
        try:
            # Здесь можно добавить проверки для внешних сервисов
            health_status["services"][service] = {"status": "unknown"}
        except Exception as e:
            health_status["services"][service] = {
                "status": "error",
                "error": str(e)
            }
    
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=health_status)

@router.get("/ready")
async def readiness_check(
    db = Depends(get_db),
    redis_client = Depends(get_redis)
) -> JSONResponse:
    """
    Проверка готовности приложения к приему запросов
    """
    try:
        # Проверка что все необходимые сервисы доступны
        db.execute(text("SELECT 1"))
        redis_client.ping()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready", "timestamp": time.time()}
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "error": str(e), "timestamp": time.time()}
        )

@router.get("/live")
async def liveness_check() -> JSONResponse:
    """
    Проверка что приложение запущено и отвечает
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "alive", "timestamp": time.time()}
    )

# Дополнительные эндпоинты для специфичных проверок

@router.get("/database")
async def database_health(db = Depends(get_db)) -> JSONResponse:
    """Проверка здоровья только базы данных"""
    try:
        start_time = time.time()
        result = db.execute(text("SELECT version(), now()")).fetchone()
        response_time = (time.time() - start_time) * 1000
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "database_version": result[0] if result else "unknown",
                "current_time": str(result[1]) if result else "unknown",
                "response_time_ms": round(response_time, 2),
                "timestamp": time.time()
            }
        )
    except SQLAlchemyError as e:
        logger.error(f"Database specific health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

@router.get("/cache")
async def cache_health(redis_client = Depends(get_redis)) -> JSONResponse:
    """Проверка здоровья только кэша/Redis"""
    try:
        start_time = time.time()
        info = redis_client.info()
        response_time = (time.time() - start_time) * 1000
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "version": info.get("redis_version", "unknown"),
                "used_memory_mb": round(info.get("used_memory_rss", 0) / 1024 / 1024, 2),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_days": round(info.get("uptime_in_days", 0), 2),
                "response_time_ms": round(response_time, 2),
                "timestamp": time.time()
            }
        )
    except (redis.ConnectionError, redis.TimeoutError) as e:
        logger.error(f"Cache specific health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )