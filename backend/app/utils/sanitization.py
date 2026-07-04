"""
Утилиты для санитизации входных данных
Функции для очистки и проверки пользовательского ввода
"""

import html
import re
from typing import Union


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Санитизация строкового ввода

    Args:
        text: Входная строка
        max_length: Максимальная длина строки

    Returns:
        Очищенная строка
    """
    if not text:
        return ""

    # Ограничиваем длину
    if len(text) > max_length:
        text = text[:max_length]

    # Экранируем HTML теги
    text = html.escape(text)

    # Удаляем потенциально опасные символы
    # Оставляем только безопасные символы
    text = re.sub(r'[<>"\']', "", text)

    # Нормализуем пробельные символы
    return re.sub(r"\s+", " ", text).strip()


def sanitize_and_validate(value: str, field_type: str = "string", field_name: str = "поле") -> str:
    """
    Sanitize a string field and raise ValueError if it contains XSS payloads.

    Repeated across multiple API endpoints — this centralizes the pattern:
        sanitize -> is_safe_string -> raise if unsafe.

    Args:
        value: Raw input string.
        field_type: One of "string", "email", "username", "text".
        field_name: Human-readable field name for the error message.

    Returns:
        Sanitized string.

    Raises:
        ValueError: If the sanitized value contains dangerous content.
    """
    sanitizer_map = {
        "email": sanitize_email,
        "username": sanitize_username,
        "text": sanitize_text_field,
    }
    sanitizer = sanitizer_map.get(field_type, sanitize_string)
    sanitized = sanitizer(value)
    if not is_safe_string(sanitized):
        raise ValueError(f"Недопустимые символы в {field_name}")
    return sanitized


def sanitize_email(email: str) -> str:
    """
    Санитизация email адреса

    Args:
        email: Email адрес

    Returns:
        Очищенный email адрес
    """
    if not email:
        return ""

    # Ограничиваем длину
    if len(email) > 254:  # Максимальная длина email по RFC
        email = email[:254]

    # Удаляем пробельные символы
    email = email.strip()

    # Экранируем HTML теги
    return html.escape(email)


def sanitize_username(username: str) -> str:
    """
    Санитизация имени пользователя

    Args:
        username: Имя пользователя

    Returns:
        Очищенное имя пользователя
    """
    if not username:
        return ""

    # Ограничиваем длину
    if len(username) > 100:
        username = username[:100]

    # Удаляем пробельные символы
    username = username.strip()

    # Экранируем HTML теги
    username = html.escape(username)

    # Оставляем только допустимые символы (буквы, цифры, подчеркивание, дефис, точка)
    return re.sub(r"[^a-zA-Z0-9_.-]", "", username)


def sanitize_text_field(text: str, max_length: int = 5000) -> str:
    """
    Санитизация текстовых полей (описания, комментарии и т.д.)

    Args:
        text: Текстовое поле
        max_length: Максимальная длина

    Returns:
        Очищенный текст
    """
    if not text:
        return ""

    # Ограничиваем длину
    if len(text) > max_length:
        text = text[:max_length]

    # Экранируем HTML теги
    text = html.escape(text)

    # Нормализуем пробельные символы
    return re.sub(r"\s+", " ", text).strip()


def is_safe_string(text: str) -> bool:
    """
    Проверка строки на потенциально опасное XSS содержание.

    SQL инъекции не проверяются — SQLAlchemy ORM использует параметризованные
    запросы, которые уже защищают от SQLi. Проверка по ключевым словам
    (select, union, drop и т.д.) только создавала ложные срабатывания
    (например, "select a mentor", "create an account").

    Args:
        text: Проверяемая строка

    Returns:
        True если строка безопасна, False если содержит XSS payload
    """
    if not text:
        return True

    xss_patterns = [
        r"<script",
        r"javascript:",
        r"onload=",
        r"onerror=",
        r"onclick=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]

    text_lower = text.lower()
    return all(not re.search(pattern, text_lower, re.IGNORECASE) for pattern in xss_patterns)


def sanitize_input(data: Union[str, dict, list], field_type: str = "string") -> Union[str, dict, list]:
    """
    Универсальная функция санитизации входных данных

    Args:
        data: Входные данные
        field_type: Тип поля ("string", "email", "username", "text")

    Returns:
        Очищенные данные
    """
    if isinstance(data, str):
        if field_type == "email":
            return sanitize_email(data)
        elif field_type == "username":
            return sanitize_username(data)
        elif field_type == "text":
            return sanitize_text_field(data)
        else:
            return sanitize_string(data)

    elif isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Рекурсивно санитизируем значения
            sanitized[key] = sanitize_input(value, field_type)
        return sanitized

    elif isinstance(data, list):
        # Рекурсивно санитизируем элементы списка
        return [sanitize_input(item, field_type) for item in data]

    else:
        # Для других типов возвращаем как есть
        return data
