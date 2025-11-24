"""
Enhanced Health Check Module
Provides detailed system health monitoring
"""
from typing import Dict, Any
from datetime import datetime
import psutil
import platform
from sqlalchemy import text
from redis import Redis

from app.database import SessionLocal
from app.config import settings


async def check_database() -> Dict[str, Any]:
    """Проверка подключения к базе данных"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy",
            "response_time_ms": 0,  # Можно добавить замер времени
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_redis() -> Dict[str, Any]:
    """Проверка подключения к Redis"""
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        return {
            "status": "healthy",
            "response_time_ms": 0,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def get_system_info() -> Dict[str, Any]:
    """Информация о системе"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent,
        },
        "platform": platform.platform(),
        "python_version": platform.python_version(),
    }


async def get_full_health_check() -> Dict[str, Any]:
    """Полная проверка здоровья системы"""
    db_health = await check_database()
    redis_health = await check_redis()
    system_info = await get_system_info()
    
    # Определяем общий статус
    overall_status = "healthy"
    if db_health["status"] == "unhealthy" or redis_health["status"] == "unhealthy":
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": db_health,
            "redis": redis_health,
        },
        "system": system_info,
    }
