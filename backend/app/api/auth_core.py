"""
Authentication API
Обработка регистрации, входа, выхода и обновления токенов
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import get_db, rate_limit_dependency
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.tasks.celery_tasks import send_welcome_email_task
from app.utils.auth_tokens import create_access_token, create_refresh_token
from app.utils.sanitization import is_safe_string, sanitize_email, sanitize_string, sanitize_username
from app.utils.security import brute_force_protection, get_password_hash, password_validator, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Регистрация нового пользователя"""

    # Санитизация входных данных
    sanitized_email = sanitize_email(user_data.email)
    sanitized_username = sanitize_username(user_data.username)
    sanitized_full_name = sanitize_string(user_data.full_name) if user_data.full_name else None

    # Проверка на безопасность входных данных
    if not is_safe_string(sanitized_email) or not is_safe_string(sanitized_username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимые символы в email или username",
        )

    # Валидация пароля
    password_check = password_validator.validate_password(user_data.password)
    if not password_check["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Слабый пароль: {', '.join(password_check['errors'])}",
        )

    # Проверка существования пользователя
    existing_user = (
        db.query(User)
        .filter((User.email == sanitized_email) | (User.username == sanitized_username))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email или username уже существует",
        )

    # Создание нового пользователя
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=sanitized_email,
        username=sanitized_username,
        full_name=sanitized_full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=True,
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Отправка приветственного email
    try:
        send_welcome_email_task.delay(new_user.email, new_user.username)
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")

    logger.info(f"Новый пользователь зарегистрирован: {new_user.email}")

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Вход пользователя и возврат JWT токенов"""

    # Санитизация входных данных
    sanitized_email = sanitize_email(credentials.email)

    # Проверка на безопасность входных данных
    if not is_safe_string(sanitized_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимые символы в email",
        )

    # Проверка на brute-force
    if brute_force_protection.is_locked(sanitized_email):
        remaining = brute_force_protection.get_lockout_time_remaining(sanitized_email)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Слишком много неудачных попыток. Попробуйте через {remaining} секунд",
        )

    # Поиск пользователя по email
    user = db.query(User).filter(User.email == sanitized_email).first()

    if not user:
        brute_force_protection.record_failed_attempt(sanitized_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    # Проверка пароля
    password_valid = verify_password(credentials.password, user.hashed_password)

    if not password_valid:
        brute_force_protection.record_failed_attempt(sanitized_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учетная запись пользователя неактивна",
        )

    # Успешный вход - сброс попыток
    brute_force_protection.reset_attempts(sanitized_email)

    # Создание токенов
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        },
        expires_delta=access_token_expires,
        token_type="access",
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # Set httpOnly cookie для refresh token (защита от XSS)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=7 * 24 * 60 * 60
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Обновление токена доступа с помощью refresh токена из httpOnly cookie"""

    from app.utils.auth_tokens import decode_token

    # Read refresh token from httpOnly cookie for security
    token_value = request.cookies.get("refresh_token")
    if not token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует refresh токен",
        )

    # Декодируем токен
    payload = decode_token(token_value, token_type="refresh")

    # Преобразуем sub из строки в int с проверкой на None
    sub_value = payload.get("sub")
    if sub_value is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен: отсутствует идентификатор пользователя",
        )

    try:
        user_id = int(sub_value)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен: некорректный идентификатор пользователя",
        ) from None

    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен",
        )

    # Создание нового токена доступа
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        },
        expires_delta=access_token_expires,
        token_type="access",
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=token_value,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(response: Response):
    """Выход пользователя — удаление refresh token cookie"""
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
    )
    return {"message": "Успешный выход из системы"}
