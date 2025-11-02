"""
Утилиты для санитизации входных данных
Функции для очистки и проверки пользовательского ввода
"""

import re
import html
from typing import Optional, Union


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
    text = re.sub(r'[<>"\']', '', text)
    
    # Нормализуем пробельные символы
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


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
    email = html.escape(email)
    
    return email


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
    username = re.sub(r'[^a-zA-Z0-9_.-]', '', username)
    
    return username


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
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def is_safe_string(text: str) -> bool:
    """
    Проверка строки на потенциально опасное содержание
    
    Args:
        text: Проверяемая строка
        
    Returns:
        True если строка безопасна, False если содержит опасное содержание
    """
    if not text:
        return True
    
    # Проверяем на наличие SQL инъекций
    sql_patterns = [
        r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b',
        r'--',
        r';',
        r'\/\*',
        r'\*\/',
    ]
    
    text_lower = text.lower()
    for pattern in sql_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False
    
    # Проверяем на наличие XSS
    xss_patterns = [
        r'<script',
        r'javascript:',
        r'onload=',
        r'onerror=',
        r'onclick=',
        r'<iframe',
        r'<object',
        r'<embed',
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False
    
    return True


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