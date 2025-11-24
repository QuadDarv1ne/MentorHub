"""
Утилиты безопасности
Включает: хеширование паролей, валидацию, защиту от brute-force, токены
"""

import bcrypt
import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


# ===== Базовые функции хеширования =====

def get_password_hash(password: str) -> str:
    """Хеширование пароля с использованием bcrypt"""
    # Конвертируем в bytes и обрезаем до 72 байт, если нужно
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Генерируем соль и хешируем пароль
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Возвращаем как строку (b'...' формат)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля по его хешу"""
    try:
        password_bytes = plain_password.encode('utf-8')
        # Обрезаем до 72 байт, если нужно
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ===== Валидация паролей =====

class PasswordValidator:
    """Валидатор паролей с проверкой на надёжность"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    COMMON_PASSWORDS = [
        'password', '123456', '12345678', 'qwerty', 'abc123',
        'monkey', '1234567', 'letmein', 'trustno1', 'dragon',
        'baseball', 'iloveyou', 'master', 'sunshine', 'ashley',
        'bailey', 'passw0rd', 'shadow', '123123', '654321'
    ]
    
    @classmethod
    def validate_password(cls, password: str) -> Dict[str, any]:
        """Валидация пароля"""
        result = {
            'is_valid': True,
            'errors': [],
            'strength': 0,
            'strength_label': ''
        }
        
        if len(password) < cls.MIN_LENGTH:
            result['errors'].append(f'Минимум {cls.MIN_LENGTH} символов')
            result['is_valid'] = False
        
        if len(password) > cls.MAX_LENGTH:
            result['errors'].append(f'Максимум {cls.MAX_LENGTH} символов')
            result['is_valid'] = False
            return result
        
        if password.lower() in cls.COMMON_PASSWORDS:
            result['errors'].append('Слишком простой пароль')
            result['is_valid'] = False
            return result
        
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        complexity_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if complexity_score < 3:
            result['errors'].append('Используйте заглавные/строчные буквы, цифры, спецсимволы')
            result['is_valid'] = False
        
        strength = min(len(password) * 4, 40) + complexity_score * 15
        strength += min(len(set(password)) * 2, 20)
        result['strength'] = min(strength, 100)
        
        if result['strength'] < 40:
            result['strength_label'] = 'Слабый'
        elif result['strength'] < 70:
            result['strength_label'] = 'Средний'
        elif result['strength'] < 90:
            result['strength_label'] = 'Сильный'
        else:
            result['strength_label'] = 'Очень сильный'
        
        return result
    
    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """Генерация надёжного пароля"""
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
        return ''.join(secrets.choice(alphabet) for _ in range(length))


# ===== Защита от brute-force =====

class BruteForceProtection:
    """Защита от brute-force атак"""
    
    def __init__(
        self,
        max_attempts: int = 5,
        lockout_duration: int = 900,  # 15 минут
        cleanup_interval: int = 3600
    ):
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        self.cleanup_interval = cleanup_interval
        self.login_attempts = defaultdict(list)
        self.lockouts = {}
        self.last_cleanup = datetime.utcnow()
    
    def record_failed_attempt(self, identifier: str):
        """Записать неудачную попытку входа"""
        now = datetime.utcnow()
        self._cleanup_old_attempts(identifier, now)
        self.login_attempts[identifier].append(now)
        
        if len(self.login_attempts[identifier]) >= self.max_attempts:
            self.lockouts[identifier] = now + timedelta(seconds=self.lockout_duration)
            logger.warning(f"Account locked: {identifier}")
    
    def is_locked(self, identifier: str) -> bool:
        """Проверка блокировки"""
        if identifier not in self.lockouts:
            return False
        
        now = datetime.utcnow()
        if now < self.lockouts[identifier]:
            return True
        else:
            del self.lockouts[identifier]
            self.login_attempts[identifier] = []
            return False
    
    def get_lockout_time_remaining(self, identifier: str) -> Optional[int]:
        """Оставшееся время блокировки в секундах"""
        if identifier not in self.lockouts:
            return None
        
        now = datetime.utcnow()
        if now < self.lockouts[identifier]:
            return int((self.lockouts[identifier] - now).total_seconds())
        return None
    
    def reset_attempts(self, identifier: str):
        """Сброс попыток"""
        if identifier in self.login_attempts:
            del self.login_attempts[identifier]
        if identifier in self.lockouts:
            del self.lockouts[identifier]
    
    def _cleanup_old_attempts(self, identifier: str, now: datetime):
        """Очистка старых попыток"""
        cutoff_time = now - timedelta(seconds=self.lockout_duration)
        if identifier in self.login_attempts:
            self.login_attempts[identifier] = [
                attempt for attempt in self.login_attempts[identifier]
                if attempt > cutoff_time
            ]


# ===== Токены и сессии =====

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
    
    _tokens = {}
    
    @classmethod
    def generate_token(cls, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=2)
        cls._tokens[token] = (user_id, expires_at)
        return token
    
    @classmethod
    def validate_token(cls, token: str, user_id: int) -> bool:
        if token not in cls._tokens:
            return False
        
        stored_user_id, expires_at = cls._tokens[token]
        
        if datetime.utcnow() > expires_at:
            del cls._tokens[token]
            return False
        
        return stored_user_id == user_id
    
    @classmethod
    def remove_token(cls, token: str):
        if token in cls._tokens:
            del cls._tokens[token]


# Singleton экземпляры
password_validator = PasswordValidator()
brute_force_protection = BruteForceProtection()
secure_token_manager = SecureTokenManager()
csrf_protection = CSRFProtection()