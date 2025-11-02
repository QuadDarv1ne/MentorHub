"""
Утилиты безопасности
Хеширование и проверка паролей
"""

import bcrypt
from typing import Optional


def get_password_hash(password: str) -> str:
    """Хеширование пароля с использованием bcrypt"""
    # Конвертируем в bytes и хешируем
    password_bytes = password.encode('utf-8')
    # Генерируем соль и хешируем пароль
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Возвращаем как строку (b'...' формат)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля по его хешу"""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

