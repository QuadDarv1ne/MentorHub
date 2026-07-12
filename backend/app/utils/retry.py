"""
Retry utilityies for external API calls
"""

import asyncio
import logging
import time
from collections.abc import Callable
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_exception(
    exceptions: tuple[type[Exception], ...] = (Exception,),
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    retry_callback: Callable | None = None,
) -> Callable:
    """
    Декоратор для повторных попыток выполнения функции при возникновении исключений.

    Args:
        exceptions: Кортеж исключений для отлова
        max_retries: Максимальное количество попыток
        delay: Начальная задержка между попытками (секунды)
        backoff: Множитель для увеличения задержки (exponential backoff)
        retry_callback: Callback функция вызывается перед каждой повторной попыткой

    Usage:
        @retry_on_exception(
            exceptions=(ConnectionError, TimeoutError),
            max_retries=3,
            delay=1.0,
            backoff=2.0
        )
        def call_external_api():
            # код
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            current_delay = delay
            last_exception: Exception | None = None

            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"{func.__name__} succeeded after {attempt + 1} attempts")
                    return result
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        if retry_callback:
                            retry_callback(e, attempt, current_delay)
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts: {e}"
                        )

            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Unexpected: no exception caught in retry loop")

        return wrapper

    return decorator


async def retry_on_exception_async(
    exceptions: tuple[type[Exception], ...] = (Exception,),
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    retry_callback: Callable | None = None,
) -> Callable:
    """
    Асинхронный декоратор для повторных попыток выполнения функции.

    Args:
        exceptions: Кортеж исключений для отлова
        max_retries: Максимальное количество попыток
        delay: Начальная задержка между попытками (секунды)
        backoff: Множитель для увеличения задержки (exponential backoff)
        retry_callback: Callback функция вызывается перед каждой повторной попыткой

    Usage:
        @retry_on_exception_async(
            exceptions=(ConnectionError, TimeoutError),
            max_retries=3,
            delay=1.0,
            backoff=2.0
        )
        async def call_external_api():
            # код
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: object, **kwargs: object) -> object:
            current_delay = delay
            last_exception: Exception | None = None

            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"{func.__name__} succeeded after {attempt + 1} attempts")
                    return result
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        if retry_callback:
                            retry_callback(e, attempt, current_delay)
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts: {e}"
                        )

            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Unexpected: no exception caught in async retry loop")

        return wrapper

    return decorator
