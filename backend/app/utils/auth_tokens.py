"""
JWT токены для аутентификации
Создание и валидация access и refresh токенов
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from app.config import settings


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
) -> str:
    """
    Создание JWT access токена с audience и issuer validation

    Args:
        data: Данные для кодирования (sub, email, role)
        expires_delta: Время жизни токена
        token_type: Тип токена (access/refresh)

    Returns:
        Закодированный JWT токен
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "aud": "mentorhub",
        "iss": "mentorhub-api",
        "type": token_type,
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создание JWT refresh токена

    Args:
        data: Данные для кодирования (sub)
        expires_delta: Время жизни токена

    Returns:
        Закодированный JWT refresh токен
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return create_access_token(
        data=data,
        expires_delta=expires_delta,
        token_type="refresh"
    )


def decode_token(token: str, token_type: str = "access") -> dict:
    """
    Декодирование и валидация JWT токена

    Args:
        token: JWT токен
        token_type: Ожидаемый тип токена

    Returns:
        Декодированный payload токена

    Raises:
        HTTPException: Если токен невалиден или истек
    """
    from fastapi import HTTPException, status

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience="mentorhub",
            issuer="mentorhub-api",
            options={"require": ["aud", "iss", "exp", "type"]},
        )

        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный тип токена",
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{'Access' if token_type == 'access' else 'Refresh'} токен истек",
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Неверный {'access' if token_type == 'access' else 'refresh'} токен",
        ) from None
