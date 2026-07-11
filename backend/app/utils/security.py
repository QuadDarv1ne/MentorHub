"""
Утилиты безопасности
Хеширование паролей, валидация, защита от brute-force, токены
"""

import hashlib
import logging
import re
import secrets
import time
from typing import Any, Dict, Optional

import bcrypt
import jwt

from app.config import settings
from app.constants import (
    COMMON_PASSWORDS,
    LOCKOUT_DURATION_SECONDS,
    MAX_LOGIN_ATTEMPTS,
    PASSWORD_ALPHABET,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
)

logger = logging.getLogger(__name__)

# Redis client for BruteForceProtection (lazy init)
_redis_client = None


def _get_redis():
    """Get or create sync Redis client for brute-force protection."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis as sync_redis
        redis_url = getattr(settings, "REDIS_URL", None)
        if redis_url:
            _redis_client = sync_redis.from_url(redis_url, decode_responses=True)
            _redis_client.ping()
            logger.info("BruteForceProtection connected to Redis")
            return _redis_client
    except Exception as e:
        logger.debug(f"Redis unavailable for BruteForceProtection: {e}")
    return None


def decode_access_token(token: str) -> Dict:
    """Декодирование access токена с audience/issuer validation"""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience="mentorhub",
            issuer="mentorhub-api",
            options={"require": ["aud", "iss", "exp"]},
        )
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
    def validate_password(cls, password: str) -> Dict[str, Any]:
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
    """Защита от brute-force атак — Redis-backed, multi-worker safe.

    Falls back to in-memory when Redis is unavailable (single-worker only).
    """

    def __init__(
        self,
        max_attempts: int = MAX_LOGIN_ATTEMPTS,
        lockout_duration: int = LOCKOUT_DURATION_SECONDS,
    ):
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        # In-memory fallback (single-worker only)
        self._attempts: Dict[str, list] = {}
        self._lockouts: Dict[str, float] = {}

    def record_failed_attempt(self, identifier: str):
        """Записать неудачную попытку входа"""
        r = _get_redis()
        now = time.time()
        key = f"bf:attempts:{identifier}"
        lockout_key = f"bf:lockout:{identifier}"

        if r:
            try:
                pipe = r.pipeline()
                pipe.zadd(key, {str(now): now})
                pipe.zremrangebyscore(key, 0, now - self.lockout_duration)
                pipe.zcard(key)
                pipe.expire(key, self.lockout_duration)
                results = pipe.execute()
                count = results[2]

                if count >= self.max_attempts:
                    r.setex(lockout_key, self.lockout_duration, str(now + self.lockout_duration))
                    r.delete(key)
                    logger.warning(f"Account locked (Redis): {identifier}")
                return
            except Exception as e:
                logger.debug(f"Redis brute-force tracking failed, using memory: {e}")

        # In-memory fallback
        cutoff = now - self.lockout_duration
        attempts = self._attempts.get(identifier, [])
        attempts = [t for t in attempts if t > cutoff]
        attempts.append(now)
        self._attempts[identifier] = attempts

        if len(attempts) >= self.max_attempts:
            self._lockouts[identifier] = now + self.lockout_duration
            logger.warning(f"Account locked (memory): {identifier}")

    def is_locked(self, identifier: str) -> bool:
        """Проверка блокировки"""
        r = _get_redis()
        lockout_key = f"bf:lockout:{identifier}"

        if r:
            try:
                val = r.get(lockout_key)
                if val:
                    return True
                return False
            except Exception:
                pass

        # In-memory fallback
        lockout_until = self._lockouts.get(identifier)
        if lockout_until is None:
            return False
        now = time.time()
        if now < lockout_until:
            return True
        del self._lockouts[identifier]
        self._attempts.pop(identifier, None)
        return False

    def get_lockout_time_remaining(self, identifier: str) -> Optional[int]:
        """Оставшееся время блокировки в секундах"""
        r = _get_redis()
        lockout_key = f"bf:lockout:{identifier}"

        if r:
            try:
                ttl = r.ttl(lockout_key)
                if ttl > 0:
                    return ttl
                return None
            except Exception:
                pass

        # In-memory fallback
        lockout_until = self._lockouts.get(identifier)
        if lockout_until is None:
            return None
        now = time.time()
        if now < lockout_until:
            return int(lockout_until - now)
        return None

    def reset_attempts(self, identifier: str):
        """Сброс попыток"""
        r = _get_redis()
        if r:
            try:
                r.delete(f"bf:attempts:{identifier}", f"bf:lockout:{identifier}")
                return
            except Exception:
                pass
        self._attempts.pop(identifier, None)
        self._lockouts.pop(identifier, None)


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


# Singleton экземпляры
password_validator = PasswordValidator()
brute_force_protection = BruteForceProtection()
secure_token_manager = SecureTokenManager()
