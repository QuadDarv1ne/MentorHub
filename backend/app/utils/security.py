"""
Утилиты безопасности
Хеширование паролей, валидация, защита от brute-force, токены
"""

import hashlib
import logging
import re
import secrets
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import bcrypt
import jwt

from app.config import settings
from app.constants import (
    CLEANUP_INTERVAL,
    COMMON_PASSWORDS,
    LOCKOUT_DURATION_SECONDS,
    MAX_LOGIN_ATTEMPTS,
    PASSWORD_ALPHABET,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
)

logger = logging.getLogger(__name__)


def decode_access_token(token: str) -> Dict:
    """Декодирование access токена с audience/issuer validation"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience="mentorhub",
            issuer="mentorhub-api",
            options={"require": ["aud", "iss", "exp"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired") from None
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token") from None


def get_password_hash(password: str) -> str:
    """Хеширование пароля с использованием bcrypt"""
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля по его хешу"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


class PasswordValidator:
    """Валидатор паролей с проверкой на надёжность"""

    MIN_LENGTH = PASSWORD_MIN_LENGTH
    MAX_LENGTH = PASSWORD_MAX_LENGTH
    COMMON_PASSWORDS = COMMON_PASSWORDS

    @classmethod
    def validate_password(cls, password: str) -> Dict[str, any]:
        """Валидация пароля"""
        result = {"is_valid": True, "errors": [], "strength": 0, "strength_label": ""}

        if len(password) < cls.MIN_LENGTH:
            result["errors"].append(f"Минимум {cls.MIN_LENGTH} символов")
            result["is_valid"] = False

        if len(password) > cls.MAX_LENGTH:
            result["errors"].append(f"Максимум {cls.MAX_LENGTH} символов")
            result["is_valid"] = False
            return result

        if password.lower() in cls.COMMON_PASSWORDS:
            result["errors"].append("Слишком простой пароль")
            result["is_valid"] = False
            return result

        has_upper = bool(re.search(r"[A-Z]", password))
        has_lower = bool(re.search(r"[a-z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        complexity_score = sum([has_upper, has_lower, has_digit, has_special])

        if complexity_score < 3:
            result["errors"].append("Используйте заглавные/строчные буквы, цифры, спецсимволы")
            result["is_valid"] = False

        strength = min(len(password) * 4, 40) + complexity_score * 15 + min(len(set(password)) * 2, 20)
        result["strength"] = min(strength, 100)

        if result["strength"] < 40:
            result["strength_label"] = "Слабый"
        elif result["strength"] < 70:
            result["strength_label"] = "Средний"
        elif result["strength"] < 90:
            result["strength_label"] = "Сильный"
        else:
            result["strength_label"] = "Очень сильный"

        return result

    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """Генерация надёжного пароля"""
        return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(length))


class BruteForceProtection:
    """Защита от brute-force атак"""

    def __init__(
        self,
        max_attempts: int = MAX_LOGIN_ATTEMPTS,
        lockout_duration: int = LOCKOUT_DURATION_SECONDS,
        cleanup_interval: int = CLEANUP_INTERVAL
    ):
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        self.cleanup_interval = cleanup_interval
        self.login_attempts = defaultdict(list)
        self.lockouts = {}
        self.last_cleanup = datetime.now(timezone.utc)

    def record_failed_attempt(self, identifier: str):
        """Записать неудачную попытку входа"""
        now = datetime.now(timezone.utc)
        self._cleanup_old_attempts(identifier, now)
        self.login_attempts[identifier].append(now)

        if len(self.login_attempts[identifier]) >= self.max_attempts:
            self.lockouts[identifier] = now + timedelta(seconds=self.lockout_duration)
            logger.warning(f"Account locked: {identifier}")

    def is_locked(self, identifier: str) -> bool:
        """Проверка блокировки"""
        if identifier not in self.lockouts:
            return False
        now = datetime.now(timezone.utc)
        if now < self.lockouts[identifier]:
            return True
        del self.lockouts[identifier]
        self.login_attempts[identifier] = []
        return False

    def get_lockout_time_remaining(self, identifier: str) -> Optional[int]:
        """Оставшееся время блокировки в секундах"""
        if identifier not in self.lockouts:
            return None
        now = datetime.now(timezone.utc)
        if now < self.lockouts[identifier]:
            return int((self.lockouts[identifier] - now).total_seconds())
        return None

    def reset_attempts(self, identifier: str):
        """Сброс попыток"""
        self.login_attempts.pop(identifier, None)
        self.lockouts.pop(identifier, None)

    def _cleanup_old_attempts(self, identifier: str, now: datetime):
        """Очистка старых попыток"""
        cutoff = now - timedelta(seconds=self.lockout_duration)
        self.login_attempts[identifier] = [
            attempt for attempt in self.login_attempts[identifier] if attempt > cutoff
        ]


class SecureTokenManager:
    """Управление безопасными токенами"""

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def generate_api_key() -> str:
        return f"mh_{secrets.token_urlsafe(40)}"


class CSRFProtection:
    """Защита от CSRF атак"""

    _tokens: Dict[str, tuple] = {}

    @classmethod
    def generate_token(cls, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
        cls._tokens[token] = (user_id, expires_at)
        return token

    @classmethod
    def validate_token(cls, token: str, user_id: int) -> bool:
        if token not in cls._tokens:
            return False
        stored_user_id, expires_at = cls._tokens[token]
        if datetime.now(timezone.utc) > expires_at:
            del cls._tokens[token]
            return False
        return stored_user_id == user_id

    @classmethod
    def remove_token(cls, token: str):
        cls._tokens.pop(token, None)


# Singleton экземпляры
password_validator = PasswordValidator()
brute_force_protection = BruteForceProtection()
secure_token_manager = SecureTokenManager()
csrf_protection = CSRFProtection()
