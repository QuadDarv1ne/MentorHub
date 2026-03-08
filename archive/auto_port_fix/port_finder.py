"""
Автоматический поиск свободного порта
=====================================

Этот модуль предоставляет функционал для автоматического определения
свободного порта перед запуском сервера.

Использование:
    from port_finder import find_free_port, get_port_with_fallback
    
    # Найти свободный порт, начиная с 8000
    port = find_free_port(start_port=8000)
    
    # Получить порт с fallback на следующий свободный
    port = get_port_with_fallback(preferred_port=8000)
"""

import socket
import os
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


def is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """
    Проверить, свободен ли порт.
    
    Args:
        port: Номер порта для проверки
        host: Хост для привязки (по умолчанию 0.0.0.0)
    
    Returns:
        True если порт свободен, False если занят
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def find_free_port(
    start_port: int = 8000,
    max_attempts: int = 100,
    host: str = "0.0.0.0",
    exclude_ports: Optional[List[int]] = None
) -> int:
    """
    Найти первый свободный порт, начиная с start_port.
    
    Args:
        start_port: Начальный порт для поиска
        max_attempts: Максимальное количество попыток
        host: Хост для проверки
        exclude_ports: Список портов, которые нужно пропустить
    
    Returns:
        Номер свободного порта
    
    Raises:
        RuntimeError: Если свободный порт не найден
    """
    exclude_ports = exclude_ports or []
    
    for port in range(start_port, start_port + max_attempts):
        if port in exclude_ports:
            continue
            
        if is_port_available(port, host):
            logger.info(f"✅ Найден свободный порт: {port}")
            return port
    
    raise RuntimeError(
        f"Не удалось найти свободный порт в диапазоне {start_port}-{start_port + max_attempts}"
    )


def get_port_with_fallback(
    preferred_port: int = 8000,
    host: str = "0.0.0.0",
    max_fallback: int = 100
) -> int:
    """
    Получить порт с автоматическим fallback на следующий свободный.
    
    Если preferred_port занят, автоматически найдёт следующий свободный.
    
    Args:
        preferred_port: Предпочитаемый порт
        host: Хост для проверки
        max_fallback: Максимальное количество портов для проверки
    
    Returns:
        Номер свободного порта (может отличаться от preferred_port)
    """
    # Сначала проверяем предпочитаемый порт
    if is_port_available(preferred_port, host):
        logger.info(f"✅ Предпочитаемый порт {preferred_port} свободен")
        return preferred_port
    
    # Если занят, ищем следующий свободный
    logger.warning(f"⚠️ Порт {preferred_port} занят, поиск свободного порта...")
    return find_free_port(preferred_port + 1, max_fallback - 1, host)


def get_port_from_env(
    env_var: str = "PORT",
    default: int = 8000,
    auto_fallback: bool = True
) -> int:
    """
    Получить порт из переменной окружения с автоматическим fallback.
    
    Args:
        env_var: Имя переменной окружения
        default: Порт по умолчанию
        auto_fallback: Автоматически искать свободный порт если занят
    
    Returns:
        Номер порта
    """
    # Получаем порт из переменной окружения или используем default
    port = int(os.environ.get(env_var, default))
    
    if auto_fallback:
        return get_port_with_fallback(port)
    
    return port


def wait_for_port_release(
    port: int,
    timeout: int = 30,
    host: str = "0.0.0.0"
) -> bool:
    """
    Подождать освобождения порта (полезно при restart).
    
    Args:
        port: Порт для ожидания
        timeout: Таймаут в секундах
        host: Хост для проверки
    
    Returns:
        True если порт освободился, False если таймаут
    """
    import time
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if is_port_available(port, host):
            logger.info(f"✅ Порт {port} освободился")
            return True
        time.sleep(0.5)
    
    logger.warning(f"⚠️ Таймаут ожидания освобождения порта {port}")
    return False


# CLI утилита для тестирования
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Поиск свободного порта")
    parser.add_argument("--start", type=int, default=8000, help="Начальный порт")
    parser.add_argument("--check", type=int, help="Проверить конкретный порт")
    parser.add_argument("--env", type=str, help="Имя переменной окружения")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    if args.check:
        if is_port_available(args.check):
            print(f"Порт {args.check} свободен")
        else:
            print(f"Порт {args.check} занят")
    elif args.env:
        port = get_port_from_env(args.env)
        print(f"Порт: {port}")
    else:
        port = find_free_port(args.start)
        print(f"Свободный порт: {port}")
