"""
API endpoints для мониторинга и метрик
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.models.user import User
from app.dependencies import get_current_user
from app.utils.monitoring import performance_monitor

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics(current_user: User = Depends(get_current_user)):
    """
    Получение метрик производительности
    Доступно только администраторам
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access metrics"
        )
    
    try:
        metrics = performance_monitor.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось получить метрики")


@router.post("/metrics/reset", response_model=Dict[str, str])
async def reset_metrics(current_user: User = Depends(get_current_user)):
    """
    Сброс метрик производительности
    Доступно только администраторам
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reset metrics"
        )
    
    try:
        performance_monitor.reset_metrics()
        return {"message": "Метрики успешно сброшены"}
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось сбросить метрики")


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check():
    """
    Детальная проверка состояния системы
    Включает метрики производительности
    """
    try:
        metrics = performance_monitor.get_metrics()

        # Определение статуса на основе метрик
        status_ok = True
        issues = []

        # Проверка CPU
        if metrics["system"]["cpu_percent"] > 80:
            status_ok = False
            issues.append(f"High CPU usage: {metrics['system']['cpu_percent']}%")

        # Проверка памяти
        if metrics["system"]["memory_percent"] > 90:
            status_ok = False
            issues.append(f"High memory usage: {metrics['system']['memory_percent']}%")

        # Проверка диска
        if metrics["system"]["disk_percent"] > 90:
            status_ok = False
            issues.append(f"High disk usage: {metrics['system']['disk_percent']}%")

        # Проверка error rate
        if metrics["application"]["error_rate_percent"] > 5:
            status_ok = False
            issues.append(f"High error rate: {metrics['application']['error_rate_percent']}%")

        return {"status": "healthy" if status_ok else "degraded", "issues": issues, "metrics": metrics}

    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {"status": "error", "issues": [str(e)], "metrics": {}}
