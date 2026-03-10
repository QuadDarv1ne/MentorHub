"""
Two-Factor Authentication (2FA) routes
TOTP (Time-based One-Time Password) implementation
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import pyotp
import qrcode
import base64
from io import BytesIO

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import TwoFactorSetup, TwoFactorVerify, TwoFactorResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/2fa", tags=["2FA"])


def generate_totp_secret() -> str:
    """Генерация TOTP секрета"""
    return pyotp.random_base32()


def get_provisioning_uri(email: str, secret: str) -> str:
    """Генерация URI для QR кода"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="MentorHub")


def generate_qr_code(uri: str) -> str:
    """Генерация QR кода в Base64"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def generate_backup_codes(count: int = 10) -> list[str]:
    """Генерация backup кодов"""
    import secrets
    import string
    
    codes = []
    for _ in range(count):
        code = ''.join(secrets.choice(string.digits) for _ in range(8))
        codes.append(code)
    return codes


@router.post("/setup", response_model=TwoFactorResponse)
async def setup_2fa(
    setup_data: TwoFactorSetup,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Настройка двухфакторной аутентификации
    
    Возвращает QR код и секрет для настройки в приложении аутентификации
    """
    if not setup_data.enabled:
        # Отключение 2FA
        current_user.two_factor_enabled = False
        current_user.two_factor_secret = None
        db.commit()
        
        logger.info(f"2FA disabled for user {current_user.id}")
        return TwoFactorResponse(enabled=False)
    
    # Генерация нового секрета
    secret = generate_totp_secret()
    current_user.two_factor_secret = secret
    db.commit()
    
    # Генерация QR кода
    uri = get_provisioning_uri(current_user.email, secret)
    qr_code = generate_qr_code(uri)
    
    # Генерация backup кодов (не сохраняем, показываем только один раз)
    backup_codes = generate_backup_codes()
    
    logger.info(f"2FA setup initiated for user {current_user.id}")
    
    return TwoFactorResponse(
        enabled=True,
        qr_code=qr_code,
        secret=secret,
        backup_codes=backup_codes
    )


@router.post("/verify", response_model=TwoFactorResponse)
async def verify_2fa(
    verify_data: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Верификация 2FA кода после настройки
    
    Подтверждает что пользователь правильно настроил приложение аутентификации
    """
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not set up. Call /setup first."
        )
    
    # Верификация кода
    totp = pyotp.TOTP(current_user.two_factor_secret)
    
    if not totp.verify(verify_data.code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code"
        )
    
    # Включаем 2FA
    current_user.two_factor_enabled = True
    db.commit()
    
    logger.info(f"2FA enabled for user {current_user.id}")
    
    return TwoFactorResponse(enabled=True)


@router.post("/disable", response_model=TwoFactorResponse)
async def disable_2fa(
    verify_data: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отключение двухфакторной аутентификации
    
    Требует текущий 2FA код для подтверждения
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    # Верификация кода
    totp = pyotp.TOTP(current_user.two_factor_secret)
    
    if not totp.verify(verify_data.code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code"
        )
    
    # Отключаем 2FA
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    db.commit()
    
    logger.info(f"2FA disabled for user {current_user.id}")
    
    return TwoFactorResponse(enabled=False)


@router.get("/status", response_model=TwoFactorResponse)
async def get_2fa_status(
    current_user: User = Depends(get_current_user)
):
    """
    Получение статуса 2FA
    
    Возвращает включена ли двухфакторная аутентификация
    """
    return TwoFactorResponse(enabled=current_user.two_factor_enabled or False)


@router.post("/verify-login")
async def verify_2fa_login(
    verify_data: TwoFactorVerify,
    temp_token: str,
    db: Session = Depends(get_db)
):
    """
    Верификация 2FA при входе
    
    Используется временный токен после успешной проверки пароля
    """
    from app.api.auth import create_access_token
    from app.config import settings
    from datetime import timedelta
    import jwt
    
    try:
        # Декодируем временный токен
        payload = jwt.decode(temp_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid temporary token"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.two_factor_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is not enabled for this user"
            )
        
        # Верификация 2FA кода
        totp = pyotp.TOTP(user.two_factor_secret)
        
        if not totp.verify(verify_data.code, valid_window=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )
        
        # Создаём финальные токены
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
        
        logger.info(f"2FA login successful for user {user.id}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Temporary token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid temporary token"
        )
