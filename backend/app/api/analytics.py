"""
Analytics API endpoints
Аналитика и статистика платформы
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, require_admin
from app.models.user import User
from app.services.analytics import AnalyticsService
from app.utils.cache import cache_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/analytics/platform")
@cache_response(ttl=300)  # 5 минут кэш
async def get_platform_analytics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Общая статистика платформы (только для админов)
    
    Returns:
        Ключевые метрики платформы
    """
    try:
        analytics = AnalyticsService(db)
        stats = analytics.get_platform_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting platform analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статистики"
        )


@router.get("/analytics/user-growth")
@cache_response(ttl=3600)  # 1 час кэш
async def get_user_growth(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    График роста пользователей
    
    Query params:
        - days: Количество дней для анализа (1-365)
    """
    try:
        analytics = AnalyticsService(db)
        growth_data = analytics.get_user_growth(days)
        return {
            "period_days": days,
            "data": growth_data
        }
    except Exception as e:
        logger.error(f"Error getting user growth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных о росте"
        )


@router.get("/analytics/sessions")
@cache_response(ttl=600)  # 10 минут кэш
async def get_session_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Аналитика по сессиям
    
    Query params:
        - days: Количество дней для анализа (1-365)
    """
    try:
        analytics = AnalyticsService(db)
        session_data = analytics.get_session_analytics(days)
        return {
            "period_days": days,
            "analytics": session_data
        }
    except Exception as e:
        logger.error(f"Error getting session analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении аналитики сессий"
        )


@router.get("/analytics/courses")
@cache_response(ttl=600)  # 10 минут кэш
async def get_course_analytics(
    course_id: Optional[int] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Анализ производительности курсов
    
    Query params:
        - course_id: ID курса (опционально)
    """
    try:
        analytics = AnalyticsService(db)
        course_data = analytics.get_course_performance(course_id)
        return course_data
    except Exception as e:
        logger.error(f"Error getting course analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении аналитики курсов"
        )


@router.get("/analytics/revenue")
@cache_response(ttl=600)  # 10 минут кэш
async def get_revenue_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Аналитика по доходам
    
    Query params:
        - days: Количество дней для анализа (1-365)
    """
    try:
        analytics = AnalyticsService(db)
        revenue_data = analytics.get_revenue_analytics(days)
        return {
            "period_days": days,
            "analytics": revenue_data
        }
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении финансовой аналитики"
        )


@router.get("/analytics/user/{user_id}/engagement")
async def get_user_engagement(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Анализ вовлеченности пользователя
    
    Пользователь может смотреть только свою статистику,
    админы могут смотреть любую.
    """
    # Проверка прав доступа
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра статистики"
        )
    
    try:
        analytics = AnalyticsService(db)
        engagement_data = analytics.get_user_engagement(user_id)
        return engagement_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting user engagement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статистики пользователя"
        )


@router.get("/analytics/me/engagement")
async def get_my_engagement(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить статистику вовлеченности текущего пользователя
    """
    try:
        analytics = AnalyticsService(db)
        engagement_data = analytics.get_user_engagement(current_user.id)
        return engagement_data
    except Exception as e:
        logger.error(f"Error getting user engagement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении вашей статистики"
        )
