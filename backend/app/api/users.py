"""
Роуты пользователей
Обработка операций с профилем пользователя
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db, rate_limit_dependency
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.cache import cached
from app.utils.sanitization import sanitize_and_validate

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

    # Санитизация и валидация входных данных
    try:
        sanitized_full_name = sanitize_and_validate(user_update.full_name, field_name="имени") if user_update.full_name is not None else None
        sanitized_avatar_url = sanitize_and_validate(user_update.avatar_url, field_name="URL аватара") if user_update.avatar_url is not None else None
        sanitized_username = sanitize_and_validate(user_update.username, field_type="username", field_name="username") if user_update.username is not None else None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

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

    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении профиля",
        ) from e


@router.get("/{user_id}", response_model=UserResponse)
@cached(ttl=600, key_prefix="user_detail")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
    current_user: User = Depends(get_current_user)
):
    """Получить пользователя по ID (требует авторизации)"""
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный ID пользователя",
        )

    # Пользователи могут видеть только свой профиль, админы - все
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён",
        )

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
