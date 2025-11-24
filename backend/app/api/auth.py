"""
Роуты аутентификации
Обработка регистрации, входа, выхода и обновления токенов
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import jwt

from app.config import settings
from app.dependencies import get_db, rate_limit_dependency
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.utils.security import verify_password, get_password_hash, brute_force_protection, password_validator
from app.utils.sanitization import sanitize_email, sanitize_username, sanitize_string, is_safe_string

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создание JWT токена доступа"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
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
        db.query(User).filter((User.email == sanitized_email) | (User.username == sanitized_username)).first()
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
        is_verified=False,  # Требуется верификация email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Новый пользователь зарегистрирован: {new_user.email}")

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
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
        logger.info(f"User not found for email: {sanitized_email}")
        brute_force_protection.record_failed_attempt(sanitized_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    logger.info(f"User found: {user.email}")
    logger.info(f"Stored hashed password: {user.hashed_password}")
    logger.info(f"Provided password: {credentials.password}")

    # Verify password
    password_valid = verify_password(credentials.password, user.hashed_password)
    logger.info(f"Password verification result: {password_valid}")

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
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        data={
            "sub": str(user.id),  # JWT требует строку для sub
            "email": user.email,
            "role": user.role.value,
        },
        expires_delta=access_token_expires,
    )

    refresh_token = create_access_token(
        data={
            "sub": str(user.id),  # JWT требует строку для sub
            "type": "refresh",
        },
        expires_delta=refresh_token_expires,
    )

    logger.info(f"Пользователь вошел в систему: {user.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Обновление токена доступа с помощью refresh токена"""

    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный тип токена",
            )

        # Преобразуем sub из строки в int с проверкой на None
        sub_value = payload.get("sub")
        if sub_value is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен: отсутствует идентификатор пользователя",
            )

        try:
            user_id = int(sub_value)  # Преобразуем в int
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен: некорректный идентификатор пользователя",
            )

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
                "sub": str(user.id),  # JWT требует строку для sub
                "email": user.email,
                "role": user.role.value,
            },
            expires_delta=access_token_expires,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Повторное использование refresh токена
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен истек",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный refresh токен",
        )


@router.post("/logout")
async def logout():
    """Выход пользователя (клиент должен удалить токены)"""
    return {"message": "Успешный выход из системы"}
