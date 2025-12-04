"""
Email verification endpoints
Подтверждение email и password reset
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import secrets

from app.config import settings
from app.dependencies import get_db
from app.models.user import User
from app.utils.email import email_service
from app.utils.security import create_access_token, get_password_hash
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)
router = APIRouter()


class EmailVerificationRequest(BaseModel):
    """Запрос на отправку verification email"""
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    """Подтверждение email с токеном"""
    token: str


class ForgotPasswordRequest(BaseModel):
    """Запрос на сброс пароля"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Сброс пароля с токеном"""
    token: str
    new_password: str


# Временное хранилище токенов (в production использовать Redis)
verification_tokens = {}
reset_tokens = {}


@router.post("/send-verification", status_code=status.HTTP_200_OK)
async def send_verification_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Отправка письма с подтверждением email"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Не раскрываем, существует ли пользователь
        return {"message": "Если email существует в системе, письмо отправлено"}
    
    if user.is_verified:
        return {"message": "Email уже подтвержден"}
    
    # Генерируем токен
    token = secrets.token_urlsafe(32)
    verification_tokens[token] = {
        "email": user.email,
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }
    
    # Отправляем email
    success = email_service.send_verification_email(
        to_email=user.email,
        username=user.username,
        token=token
    )
    
    if success:
        logger.info(f"✅ Verification email sent to {user.email}")
    else:
        logger.warning(f"⚠️ Failed to send verification email to {user.email}")
    
    return {"message": "Письмо с подтверждением отправлено"}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """Подтверждение email по токену"""
    token_data = verification_tokens.get(request.token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или истекший токен"
        )
    
    # Проверяем срок действия
    if datetime.utcnow() > token_data["expires_at"]:
        del verification_tokens[request.token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен истек"
        )
    
    # Находим пользователя
    user = db.query(User).filter(User.email == token_data["email"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Подтверждаем email
    user.is_verified = True
    db.commit()
    
    # Удаляем использованный токен
    del verification_tokens[request.token]
    
    logger.info(f"✅ Email verified for user {user.email}")
    
    return {
        "message": "Email успешно подтвержден",
        "email": user.email
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Запрос на сброс пароля"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Не раскрываем, существует ли пользователь
        return {"message": "Если email существует в системе, письмо отправлено"}
    
    # Генерируем токен
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "email": user.email,
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }
    
    # Отправляем email
    success = email_service.send_password_reset_email(
        to_email=user.email,
        username=user.username,
        token=token
    )
    
    if success:
        logger.info(f"✅ Password reset email sent to {user.email}")
    else:
        logger.warning(f"⚠️ Failed to send password reset email to {user.email}")
    
    return {"message": "Письмо для сброса пароля отправлено"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Сброс пароля по токену"""
    token_data = reset_tokens.get(request.token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или истекший токен"
        )
    
    # Проверяем срок действия
    if datetime.utcnow() > token_data["expires_at"]:
        del reset_tokens[request.token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен истек"
        )
    
    # Находим пользователя
    user = db.query(User).filter(User.email == token_data["email"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Обновляем пароль
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    # Удаляем использованный токен
    del reset_tokens[request.token]
    
    logger.info(f"✅ Password reset for user {user.email}")
    
    return {
        "message": "Пароль успешно изменен",
        "email": user.email
    }
