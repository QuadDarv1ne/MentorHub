"""
Роуты пользователей
Обработка операций с профилем пользователя
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, get_pagination, PaginationParams, rate_limit_dependency
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import PaginatedResponse
from app.utils.sanitization import sanitize_string, sanitize_username, is_safe_string
from app.utils.cache import cached, invalidate_cache, CACHE_TTL

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить профиль текущего пользователя"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить профиль текущего пользователя"""

    # Санитизация входных данных
    sanitized_full_name = sanitize_string(user_update.full_name) if user_update.full_name is not None else None
    sanitized_avatar_url = sanitize_string(user_update.avatar_url) if user_update.avatar_url is not None else None
    sanitized_username = sanitize_username(user_update.username) if user_update.username is not None else None

    # Проверка на безопасность входных данных
    if sanitized_username and not is_safe_string(sanitized_username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимые символы в username",
        )

    # Обновление полей
    if sanitized_full_name is not None:
        current_user.full_name = sanitized_full_name
    if sanitized_avatar_url is not None:
        current_user.avatar_url = sanitized_avatar_url
    if sanitized_username is not None:
        # Проверка уникальности username
        existing = db.query(User).filter(User.username == sanitized_username, User.id != current_user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username уже занят",
            )
        current_user.username = sanitized_username

    db.commit()
    db.refresh(current_user)

    logger.info(f"Профиль пользователя обновлен: {current_user.email}")
    
    # Инвалидируем кеш обновленного пользователя
    import asyncio
    asyncio.create_task(invalidate_cache(f"user_detail:{current_user.id}"))

    return current_user


@router.get("/{user_id}", response_model=UserResponse)
@cached(ttl=CACHE_TTL['user'], key_prefix="user_detail")
async def get_user(user_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить пользователя по ID"""
    # Проверка на корректность ID
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный ID пользователя",
        )

    # Оптимизация N+1: загружаем связанные данные
    from sqlalchemy.orm import joinedload
    user = db.query(User).options(
        joinedload(User.mentor_profile),
        joinedload(User.sessions_as_student),
        joinedload(User.progress_records)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return user
