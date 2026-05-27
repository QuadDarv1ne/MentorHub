"""
Дополнительные валидаторы для повышения безопасности
"""

import logging
import re

from fastapi import HTTPException, status

from app.constants import (
    EMAIL_MAX_LENGTH,
    SANITIZE_TEXT_MAX_LENGTH,
    URL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)

logger = logging.getLogger(__name__)

# Регулярные выражения для валидации
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 format
USERNAME_REGEX = re.compile(rf"^[a-zA-Z0-9_-]{{{USERNAME_MIN_LENGTH},{USERNAME_MAX_LENGTH}}}$")
URL_REGEX = re.compile(
    r"^https?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

# SQL Injection patterns
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
    r"(--|\#|\/\*|\*\/)",
    r"(\bOR\b.*=.*)",
    r"(\bAND\b.*=.*)",
    r"(;.*)",
]

# XSS patterns
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe",
    r"<object",
    r"<embed",
]


def validate_email(email: str) -> str:
    """
    Валидация email адреса

    Args:
        email: Email для проверки

    Returns:
        Нормализованный email

    Raises:
        HTTPException: Если email невалиден
    """
    email = email.strip().lower()

    if not EMAIL_REGEX.match(email):
        logger.warning(f"Invalid email format: {email}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email format",
        )

    if len(email) > EMAIL_MAX_LENGTH:  # RFC 5321
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email too long",
        )

    return email


def validate_phone(phone: str) -> str:
    """
    Валидация телефонного номера (E.164 format)

    Args:
        phone: Телефон для проверки

    Returns:
        Нормализованный телефон

    Raises:
        HTTPException: Если телефон невалиден
    """
    # Удаляем пробелы и дефисы
    phone = re.sub(r"[\s-]", "", phone)

    if not PHONE_REGEX.match(phone):
        logger.warning(f"Invalid phone format: {phone}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid phone format. Use E.164 format (e.g., +1234567890)",
        )

    return phone


def validate_username(username: str) -> str:
    """
    Валидация имени пользователя

    Args:
        username: Имя пользователя

    Returns:
        Нормализованное имя

    Raises:
        HTTPException: Если имя невалидно
    """
    username = username.strip()

    if not USERNAME_REGEX.match(username):
        logger.warning(f"Invalid username format: {username}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username must be 3-32 characters long and contain only letters, numbers, underscores, and hyphens",
        )

    # Проверка зарезервированных имен
    reserved_names = {"admin", "root", "system", "api", "www", "mail"}
    if username.lower() in reserved_names:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This username is reserved",
        )

    return username


def validate_url(url: str) -> str:
    """
    Валидация URL

    Args:
        url: URL для проверки

    Returns:
        Валидированный URL

    Raises:
        HTTPException: Если URL невалиден
    """
    url = url.strip()

    if not URL_REGEX.match(url):
        logger.warning(f"Invalid URL format: {url}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid URL format",
        )

    if len(url) > URL_MAX_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL too long",
        )

    return url


def sanitize_input(text: str, max_length: int = SANITIZE_TEXT_MAX_LENGTH) -> str:
    """
    Очистка пользовательского ввода от потенциально опасных символов

    Args:
        text: Текст для очистки
        max_length: Максимальная длина

    Returns:
        Очищенный текст

    Raises:
        HTTPException: Если обнаружены опасные паттерны
    """
    if not text:
        return text

    text = text.strip()

    # Проверка длины
    if len(text) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Input too long. Maximum {max_length} characters allowed",
        )

    # Проверка на SQL injection
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Potential SQL injection detected: {text[:100]}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input detected",
            )

    # Проверка на XSS
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Potential XSS detected: {text[:100]}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input detected",
            )

    return text


def validate_password_strength(password: str) -> None:
    """
    Проверка надежности пароля

    Args:
        password: Пароль для проверки

    Raises:
        HTTPException: Если пароль слабый
    """
    from app.constants import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH

    if len(password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long",
        )

    if len(password) > PASSWORD_MAX_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password too long",
        )

    # Проверка на наличие цифр
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one digit",
        )

    # Проверка на наличие букв
    if not re.search(r"[a-zA-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one letter",
        )

    # Проверка на наличие спецсимволов (опционально, но рекомендуется)
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        logger.info("Password without special characters - weak but allowed")
