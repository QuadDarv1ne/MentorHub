"""
Дополнительные валидаторы для повышения безопасности
"""

import re
import logging
from typing import Optional
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Регулярные выражения для валидации
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 format
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,32}$")
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

    if len(email) > 254:  # RFC 5321
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

    if len(url) > 2048:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL too long",
        )

    return url


def sanitize_input(text: str, max_length: int = 1000) -> str:
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
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long",
        )

    if len(password) > 128:
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


def validate_pagination(page: int = 1, limit: int = 10, max_limit: int = 100) -> tuple:
    """
    Валидация параметров пагинации

    Args:
        page: Номер страницы
        limit: Количество элементов на странице
        max_limit: Максимальное количество элементов

    Returns:
        Tuple[page, limit] с валидированными значениями

    Raises:
        HTTPException: Если параметры невалидны
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page must be greater than 0",
        )

    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit must be greater than 0",
        )

    if limit > max_limit:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Limit must not exceed {max_limit}",
        )

    return page, limit
