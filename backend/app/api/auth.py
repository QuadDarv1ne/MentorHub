"""
Роуты аутентификации
Обработка регистрации, входа, выхода и обновления токенов
"""

import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response
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


def create_access_token(data: dict, expires_delta: timedelta | None = None, token_type: str = "access") -> str:
    """Создание JWT токена с audience и issuer validation"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "aud": "mentorhub",
        "iss": "mentorhub-api",
        "type": token_type,
    })
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
        token_type="access",
    )

    refresh_token = create_access_token(
        data={
            "sub": str(user.id),  # JWT требует строку для sub
        },
        expires_delta=refresh_token_expires,
        token_type="refresh",
    )
    
    # Set httpOnly cookie для refresh token (защита от XSS)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Защита от XSS
        secure=settings.ENVIRONMENT == "production",  # HTTPS only в production
        samesite="strict",  # Защита от CSRF
        max_age=7 * 24 * 60 * 60  # 7 дней
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
            audience="mentorhub",
            issuer="mentorhub-api",
            options={"require": ["aud", "iss", "exp", "type"]},
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
            token_type="access",
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


# ==================== OAUTH ROUTES ====================

@router.get("/oauth/{provider}")
async def oauth_login(provider: str, response: Response):
    """
    OAuth login endpoint
    Перенаправляет на Google или GitHub для аутентификации
    """
    from authlib.integrations.starlette_client import OAuth
    from authlib.common.security import generate_token
    from starlette.responses import RedirectResponse
    
    if provider not in ["google", "github"]:
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")
    
    # Генерируем state token для защиты от CSRF
    state = generate_token(16)
    response.set_cookie(key="oauth_state", value=state, httponly=True, secure=settings.ENVIRONMENT == "production", max_age=600)
    
    if provider == "google":
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")
        
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.GOOGLE_CLIENT_ID}&"
            f"redirect_uri={settings.OAUTH_REDIRECT_URI}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile&"
            f"state={state}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        return RedirectResponse(url=google_auth_url)
    
    elif provider == "github":
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
        
        github_auth_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={settings.GITHUB_CLIENT_ID}&"
            f"redirect_uri={settings.OAUTH_REDIRECT_URI}&"
            f"scope=user:email&"
            f"state={state}"
        )
        return RedirectResponse(url=github_auth_url)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    OAuth callback endpoint
    Обрабатывает callback от Google или GitHub
    """
    import httpx
    
    # Проверяем state token
    oauth_state = response.cookies.get("oauth_state")
    if not oauth_state or oauth_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Удаляем state cookie
    response.delete_cookie("oauth_state")
    
    user_data = {}
    
    if provider == "google":
        # Получаем access token от Google
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.OAUTH_REDIRECT_URI,
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get access token from Google")
            
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            
            # Получаем данные пользователя
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_data = user_info_response.json()
    
    elif provider == "github":
        # Получаем access token от GitHub
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.OAUTH_REDIRECT_URI,
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")
            
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            
            # Получаем данные пользователя
            user_info_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/json"
                }
            )
            user_data = user_info_response.json()
            
            # Получаем email если не получен
            if "email" not in user_data:
                emails_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json"
                    }
                )
                emails = emails_response.json()
                for email_info in emails:
                    if email_info.get("primary"):
                        user_data["email"] = email_info["email"]
                        break
    
    # Извлекаем данные
    email = user_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")
    
    username = user_data.get("login") or user_data.get("name") or email.split("@")[0]
    full_name = user_data.get("name")
    avatar_url = user_data.get("avatar_url") or user_data.get("picture")
    oauth_id = str(user_data.get("id"))
    
    # Проверяем существует ли пользователь
    user = db.query(User).filter(
        (User.email == email) | ((User.oauth_provider == provider) & (User.oauth_id == oauth_id))
    ).first()
    
    if user:
        # Обновляем данные если пользователь существует
        user.avatar_url = avatar_url or user.avatar_url
        user.full_name = full_name or user.full_name
        db.commit()
        db.refresh(user)
    else:
        # Создаём нового пользователя
        # Генерируем уникальный username
        base_username = username.replace(" ", "_").lower()
        unique_username = base_username
        counter = 1
        while db.query(User).filter(User.username == unique_username).first():
            unique_username = f"{base_username}_{counter}"
            counter += 1
        
        user = User(
            email=email,
            username=unique_username,
            full_name=full_name,
            avatar_url=avatar_url,
            oauth_provider=provider,
            oauth_id=oauth_id,
            hashed_password=None,  # OAuth пользователи не имеют пароля
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,  # OAuth пользователи верифицированы
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Создаём токены
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
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        },
        expires_delta=refresh_token_expires,
        token_type="refresh",
    )
    
    # Перенаправляем на frontend с токенами
    frontend_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}&token_type=bearer&expires_in={settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}"
    return RedirectResponse(url=frontend_url)
