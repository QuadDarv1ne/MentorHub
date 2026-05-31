"""
Tests for retry utilities
"""

import pytest
import time
from unittest.mock import MagicMock, patch

from app.utils.retry import retry_on_exception, retry_on_exception_async


class TestRetryOnException:
    """Тесты для синхронного retry декоратора"""

    def test_retry_succeeds_on_first_attempt(self):
        """Тест: функция выполняется успешно с первой попытки"""
        call_count = 0

        @retry_on_exception(exceptions=(ValueError,), max_retries=3, delay=0.01)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_function()
        assert result == "success"
        assert call_count == 1

    def test_retry_succeeds_after_failures(self):
        """Тест: функция выполняется успешно после нескольких неудачных попыток"""
        call_count = 0

        @retry_on_exception(exceptions=(ValueError,), max_retries=3, delay=0.01)
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = eventually_successful_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_raises_after_max_retries(self):
        """Тест: функция выбрасывает исключение после максимального числа попыток"""
        call_count = 0

        @retry_on_exception(exceptions=(ValueError,), max_retries=3, delay=0.01)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")

        with pytest.raises(ValueError, match="Persistent error"):
            always_failing_function()

        assert call_count == 3

    def test_retry_with_custom_backoff(self):
        """Тест: retry с кастомным backoff множителем"""
        call_count = 0
        sleep_times = []

        original_sleep = time.sleep
        def mock_sleep(seconds):
            sleep_times.append(seconds)
            original_sleep(0.001)  # Небольшая задержка для реалистичности

        @retry_on_exception(exceptions=(ValueError,), max_retries=3, delay=1.0, backoff=3.0)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Error")

        with patch('time.sleep', mock_sleep), pytest.raises(ValueError):
                failing_function()

        assert call_count == 3
        assert len(sleep_times) == 2
        assert sleep_times[0] == 1.0
        assert sleep_times[1] == 3.0

    def test_retry_with_callback(self):
        """Тест: retry с callback функцией"""
        callback_called = False
        callback_args = []

        def error_callback(error, attempt, delay):
            nonlocal callback_called
            callback_called = True
            callback_args.extend([error, attempt, delay])

        call_count = 0

        @retry_on_exception(
            exceptions=(ValueError,),
            max_retries=2,
            delay=0.01,
            retry_callback=error_callback
        )
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Error")

        with pytest.raises(ValueError):
            failing_function()

        assert callback_called
        assert isinstance(callback_args[0], ValueError)
        assert callback_args[1] == 0  # attempt
        assert callback_args[2] == 0.01  # delay

    def test_retry_only_catches_specified_exceptions(self):
        """Тест: retry ловит только указанные исключения"""
        call_count = 0

        @retry_on_exception(exceptions=(ValueError,), max_retries=3, delay=0.01)
        def type_error_function():
            nonlocal call_count
            call_count += 1
            raise TypeError("Wrong exception type")

        with pytest.raises(TypeError):
            type_error_function()

        assert call_count == 1  # Не должно быть retry


@pytest.mark.asyncio
class TestRetryOnExceptionAsync:
    """Тесты для асинхронного retry декоратора"""

    async def test_async_retry_succeeds_on_first_attempt(self):
        """Тест: асинхронная функция выполняется успешно с первой попытки"""
        call_count = 0

        @retry_on_exception_async(exceptions=(ValueError,), max_retries=3, delay=0.01)
        async def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_function()
        assert result == "success"
        assert call_count == 1

    async def test_async_retry_succeeds_after_failures(self):
        """Тест: асинхронная функция выполняется успешно после нескольких неудачных попыток"""
        call_count = 0

        @retry_on_exception_async(exceptions=(ValueError,), max_retries=3, delay=0.01)
        async def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = await eventually_successful_function()
        assert result == "success"
        assert call_count == 3

    async def test_async_retry_raises_after_max_retries(self):
        """Тест: асинхронная функция выбрасывает исключение после максимального числа попыток"""
        call_count = 0

        @retry_on_exception_async(exceptions=(ValueError,), max_retries=3, delay=0.01)
        async def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")

        with pytest.raises(ValueError, match="Persistent error"):
            await always_failing_function()

        assert call_count == 3
