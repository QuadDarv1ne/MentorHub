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
    ["method", "endpoint", "exception_type"],
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

# Новые метрики для детального мониторинга
USER_SESSIONS = Gauge("mentorhub_user_sessions_total", "Active user sessions")
API_CALLS_BY_USER_ROLE = Counter(
    "mentorhub_api_calls_by_user_role_total",
    "API calls by user role",
    ["role", "endpoint"]
)
DATABASE_QUERIES = Counter(
    "mentorhub_database_queries_total",
    "Database query count",
    ["query_type", "table"]
)
DATABASE_QUERY_DURATION = Histogram(
    "mentorhub_database_query_duration_seconds",
    "Database query duration",
    ["query_type", "table"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, float("inf"))
)
CACHE_OPERATIONS = Counter(
    "mentorhub_cache_operations_total",
    "Cache operations count",
    ["operation", "cache_type"]
)
EXTERNAL_API_CALLS = Counter(
    "mentorhub_external_api_calls_total",
    "External API calls count",
    ["service", "endpoint", "status"]
)
EXTERNAL_API_DURATION = Histogram(
    "mentorhub_external_api_duration_seconds",
    "External API call duration",
    ["service", "endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, float("inf"))
)
BACKGROUND_TASKS = Counter(
    "mentorhub_background_tasks_total",
    "Background tasks count",
    ["task_type", "status"]
)
PAYMENT_TRANSACTIONS = Counter(
    "mentorhub_payment_transactions_total",
    "Payment transactions count",
    ["status", "payment_method"]
)
MESSAGES_SENT = Counter(
    "mentorhub_messages_sent_total",
    "Messages sent count",
    ["message_type"]
)
VIDEO_SESSIONS = Counter(
    "mentorhub_video_sessions_total",
    "Video sessions count",
    ["status"]
)
VIDEO_SESSION_DURATION = Histogram(
    "mentorhub_video_session_duration_seconds",
    "Video session duration",
    buckets=(60, 300, 600, 1800, 3600, 7200, float("inf"))
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
            ERROR_COUNT.labels(method=method, endpoint=endpoint, exception_type=type(e).__name__).inc()
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
                CACHE_OPERATIONS.labels(operation="hit", cache_type=cache_type).inc()
            else:
                CACHE_MISSES.labels(cache_type=cache_type).inc()
                CACHE_OPERATIONS.labels(operation="miss", cache_type=cache_type).inc()
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


def record_user_role_access(role: str, endpoint: str):
    """
    Запись доступа по роли пользователя

    Args:
        role: Роль пользователя
        endpoint: Endpoint, к которому был доступ
    """
    API_CALLS_BY_USER_ROLE.labels(role=role, endpoint=endpoint).inc()


def record_database_query(query_type: str, table: str, duration: float = 0):
    """
    Запись метрик запроса к БД

    Args:
        query_type: Тип запроса (select, insert, update, delete)
        table: Таблица
        duration: Время выполнения запроса в секундах
    """
    DATABASE_QUERIES.labels(query_type=query_type, table=table).inc()
    if duration > 0:
        DATABASE_QUERY_DURATION.labels(query_type=query_type, table=table).observe(duration)


def record_cache_operation(operation: str, cache_type: str = "redis"):
    """
    Запись операции с кэшем

    Args:
        operation: Тип операции (get, set, delete, clear)
        cache_type: Тип кэша (redis, memory)
    """
    CACHE_OPERATIONS.labels(operation=operation, cache_type=cache_type).inc()


def record_external_api_call(service: str, endpoint: str, status: str, duration: float = 0):
    """
    Запись вызова внешнего API

    Args:
        service: Сервис (stripe, agora, aws)
        endpoint: Endpoint
        status: Статус ответа
        duration: Время выполнения в секундах
    """
    EXTERNAL_API_CALLS.labels(service=service, endpoint=endpoint, status=status).inc()
    if duration > 0:
        EXTERNAL_API_DURATION.labels(service=service, endpoint=endpoint).observe(duration)


def record_background_task(task_type: str, status: str):
    """
    Запись фоновой задачи

    Args:
        task_type: Тип задачи
        status: Статус (success, failed)
    """
    BACKGROUND_TASKS.labels(task_type=task_type, status=status).inc()


def record_payment_transaction(status: str, payment_method: str):
    """
    Запись транзакции оплаты

    Args:
        status: Статус (success, failed, pending)
        payment_method: Метод оплаты (card, stripe, paypal)
    """
    PAYMENT_TRANSACTIONS.labels(status=status, payment_method=payment_method).inc()


def record_message_sent(message_type: str):
    """
    Запись отправленного сообщения

    Args:
        message_type: Тип сообщения (email, sms, notification)
    """
    MESSAGES_SENT.labels(message_type=message_type).inc()


def record_video_session(status: str, duration: float = 0):
    """
    Запись видеосессии

    Args:
        status: Статус (started, ended, failed)
        duration: Длительность в секундах
    """
    VIDEO_SESSIONS.labels(status=status).inc()
    if duration > 0 and status == "ended":
        VIDEO_SESSION_DURATION.observe(duration)