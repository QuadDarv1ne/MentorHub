"""
OAuth handlers для MentorHub
Обработка OAuth аутентификации через Google и GitHub
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
import logging

from app.config import settings
from app.dependencies import get_db
from app.models.user import User, UserRole
from app.utils.auth_tokens import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["OAuth"])


def _generate_oauth_state() -> str:
    """Генерация state token для защиты от CSRF"""
    import secrets
    return secrets.token_urlsafe(16)


def _create_oauth_response(
    user: User,
    response: Response
) -> RedirectResponse:
    """Создание редиректа с токенами на frontend"""
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        },
        token_type="access",
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
    )

    frontend_url = (
        f"{settings.FRONTEND_URL}/auth/callback?"
        f"access_token={access_token}&"
        f"refresh_token={refresh_token}&"
        f"token_type=bearer&"
        f"expires_in={settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}"
    )
    
    return RedirectResponse(url=frontend_url)


async def _handle_google_oauth(code: str, state: str, response: Response) -> dict:
    """Обработка OAuth callback от Google"""
    async with httpx.AsyncClient() as client:
        # Получаем access token
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
        return user_info_response.json()


async def _handle_github_oauth(code: str, state: str, response: Response) -> dict:
    """Обработка OAuth callback от GitHub"""
    async with httpx.AsyncClient() as client:
        # Получаем access token
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

        return user_data


@router.get("/login/{provider}")
async def oauth_login(provider: str, response: Response):
    """
    OAuth login endpoint
    Перенаправляет на Google или GitHub для аутентификации
    """
    if provider not in ["google", "github"]:
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")

    # Проверяем конфигурацию
    if provider == "google":
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")

        state = _generate_oauth_state()
        response.set_cookie(
            key="oauth_state",
            value=state,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            max_age=600
        )

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

        state = _generate_oauth_state()
        response.set_cookie(
            key="oauth_state",
            value=state,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            max_age=600
        )

        github_auth_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={settings.GITHUB_CLIENT_ID}&"
            f"redirect_uri={settings.OAUTH_REDIRECT_URI}&"
            f"scope=user:email&"
            f"state={state}"
        )
        return RedirectResponse(url=github_auth_url)


@router.get("/callback/{provider}")
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
    # Проверяем state token
    oauth_state = response.cookies.get("oauth_state")
    if not oauth_state or oauth_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Удаляем state cookie
    response.delete_cookie("oauth_state")

    # Получаем данные пользователя от провайдера
    if provider == "google":
        user_data = await _handle_google_oauth(code, state, response)
    elif provider == "github":
        user_data = await _handle_github_oauth(code, state, response)
    else:
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")

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

    # Создаём редирект с токенами
    return _create_oauth_response(user, response)
