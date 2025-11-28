"""
Prometheus метрики для мониторинга приложения
"""

import time
import logging
from typing import Callable
from functools import wraps

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

# Определение метрик
REQUEST_COUNT = Counter(
    "mentorhub_requests_total",
    "Total request count",
    ["method", "endpoint", "http_status"],
)

REQUEST_DURATION = Histogram(
    "mentorhub_request_duration_seconds",
    "Request latency",
    ["method", "endpoint"],
    buckets=(0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0, float("inf"))
)

REQUEST_IN_PROGRESS = Gauge(
    "mentorhub_requests_in_progress",
    "Requests in progress",
    ["method", "endpoint"],
)

ERROR_COUNT = Counter(
    "mentorhub_errors_total",
    "Total error count",
    ["method", "endpoint", "exception_type", "http_status"],
)

DB_CONNECTION_POOL = Gauge(
    "mentorhub_db_connection_pool",
    "Database connection pool size",
    ["pool_type"],
)

CACHE_HITS = Counter("mentorhub_cache_hits_total", "Cache hits", ["cache_type"])

CACHE_MISSES = Counter("mentorhub_cache_misses_total", "Cache misses", ["cache_type"])

# Дополнительные метрики
ACTIVE_USERS = Gauge("mentorhub_active_users", "Number of active users")

REQUEST_SIZE_BYTES = Histogram(
    "mentorhub_request_size_bytes",
    "Request size in bytes",
    ["method", "endpoint"],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, float("inf"))
)

RESPONSE_SIZE_BYTES = Histogram(
    "mentorhub_response_size_bytes",
    "Response size in bytes",
    ["method", "endpoint", "http_status"],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, float("inf"))
)

SLOW_REQUESTS = Counter(
    "mentorhub_slow_requests_total",
    "Slow requests count (over 1 second)",
    ["method", "endpoint"]
)

SECURITY_INCIDENTS = Counter(
    "mentorhub_security_incidents_total",
    "Security incidents count",
    ["incident_type", "endpoint"]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware для сбора Prometheus метрик
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = request.url.path

        # Пропускаем метрики для самого endpoint метрик
        if path == "/metrics":
            return await call_next(request)

        # Группируем пути с параметрами
        endpoint = self._get_endpoint_path(path)

        # Увеличиваем счетчик запросов в процессе
        REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

        start_time = time.time()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception as e:
            # Записываем ошибки
            ERROR_COUNT.labels(method=method, endpoint=endpoint, exception_type=type(e).__name__, http_status=500).inc()
            raise

        finally:
            # Записываем время выполнения
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            
            # Отслеживаем медленные запросы
            if duration > 1.0:
                SLOW_REQUESTS.labels(method=method, endpoint=endpoint).inc()

            # Записываем общее количество запросов
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()

            # Уменьшаем счетчик запросов в процессе
            REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()
            
            # Записываем размеры запроса и ответа
            if hasattr(request, 'headers'):
                content_length = request.headers.get('content-length', 0)
                if content_length:
                    REQUEST_SIZE_BYTES.labels(method=method, endpoint=endpoint).observe(int(content_length))
            
            if hasattr(response, 'headers'):
                response_size = response.headers.get('content-length', 0)
                if response_size:
                    RESPONSE_SIZE_BYTES.labels(method=method, endpoint=endpoint, http_status=status_code).observe(int(response_size))

    @staticmethod
    def _get_endpoint_path(path: str) -> str:
        """
        Группирует пути с параметрами для метрик

        Args:
            path: Путь запроса

        Returns:
            Обобщенный путь
        """
        # Заменяем числовые ID на {id}
        parts = path.split("/")
        normalized_parts = []

        for part in parts:
            if part.isdigit():
                normalized_parts.append("{id}")
            else:
                normalized_parts.append(part)

        return "/".join(normalized_parts)


def track_cache_hit(cache_type: str = "redis"):
    """
    Декоратор для отслеживания попаданий в кэш
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if result is not None:
                CACHE_HITS.labels(cache_type=cache_type).inc()
            else:
                CACHE_MISSES.labels(cache_type=cache_type).inc()
            return result

        return wrapper

    return decorator


async def metrics_endpoint() -> Response:
    """
    Endpoint для экспорта метрик в формате Prometheus

    Returns:
        Response с метриками
    """
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


def update_db_pool_metrics(pool_size: int, overflow: int, used: int):
    """
    Обновление метрик пула подключений к БД

    Args:
        pool_size: Размер пула
        overflow: Overflow размер
        used: Используемых подключений
    """
    DB_CONNECTION_POOL.labels(pool_type="size").set(pool_size)
    DB_CONNECTION_POOL.labels(pool_type="overflow").set(overflow)
    DB_CONNECTION_POOL.labels(pool_type="used").set(used)


def update_active_users_count(count: int):
    """
    Обновление метрики активных пользователей

    Args:
        count: Количество активных пользователей
    """
    ACTIVE_USERS.set(count)


def record_security_incident(incident_type: str, endpoint: str = "unknown"):
    """
    Запись инцидента безопасности

    Args:
        incident_type: Тип инцидента
        endpoint: Endpoint, где произошел инцидент
    """
    SECURITY_INCIDENTS.labels(incident_type=incident_type, endpoint=endpoint).inc()
