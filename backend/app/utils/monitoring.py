"""
Мониторинг производительности и метрик приложения
"""

import time
import psutil
import logging
from typing import Dict, Any
from datetime import datetime
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Монитор производительности приложения"""
    
    def __init__(self):
        self.request_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.endpoint_calls = defaultdict(int)
        self.start_time = datetime.utcnow()
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """Запись метрик запроса"""
        self.endpoint_calls[endpoint] += 1
        self.request_times[endpoint].append(duration)
        
        if status_code >= 400:
            self.error_counts[endpoint] += 1
        
        # Ограничение размера массива
        if len(self.request_times[endpoint]) > 1000:
            self.request_times[endpoint] = self.request_times[endpoint][-500:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Получение текущих метрик"""
        
        # Системные метрики
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Метрики приложения
        total_requests = sum(self.endpoint_calls.values())
        total_errors = sum(self.error_counts.values())
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # Средние времена ответа
        avg_response_times = {}
        for endpoint, times in self.request_times.items():
            if times:
                avg_response_times[endpoint] = {
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        
        # Топ медленных endpoints
        slow_endpoints = sorted(
            avg_response_times.items(),
            key=lambda x: x[1]['avg'],
            reverse=True
        )[:10]
        
        # Топ популярных endpoints
        popular_endpoints = sorted(
            self.endpoint_calls.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': uptime,
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': memory.used / (1024 * 1024),
                'memory_total_mb': memory.total / (1024 * 1024),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024 * 1024 * 1024),
                'disk_total_gb': disk.total / (1024 * 1024 * 1024),
            },
            'application': {
                'total_requests': total_requests,
                'total_errors': total_errors,
                'error_rate_percent': round(error_rate, 2),
                'requests_per_second': round(total_requests / uptime, 2) if uptime > 0 else 0,
            },
            'slow_endpoints': [
                {
                    'endpoint': endpoint,
                    'avg_ms': round(data['avg'] * 1000, 2),
                    'max_ms': round(data['max'] * 1000, 2),
                    'count': data['count']
                }
                for endpoint, data in slow_endpoints
            ],
            'popular_endpoints': [
                {'endpoint': endpoint, 'calls': count}
                for endpoint, count in popular_endpoints
            ]
        }
    
    def reset_metrics(self):
        """Сброс метрик"""
        self.request_times.clear()
        self.error_counts.clear()
        self.endpoint_calls.clear()
        self.start_time = datetime.utcnow()
        logger.info("📊 Metrics reset")


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware для мониторинга производительности"""
    
    def __init__(self, app, monitor: PerformanceMonitor):
        super().__init__(app)
        self.monitor = monitor
    
    async def dispatch(self, request: Request, call_next):
        # Пропуск метрик для health checks
        if request.url.path in ['/health', '/metrics']:
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            self.monitor.record_request(
                endpoint=request.url.path,
                duration=duration,
                status_code=response.status_code
            )
            
            # Добавление заголовка с временем обработки
            response.headers["X-Process-Time"] = f"{duration:.4f}"
            
            # Логирование медленных запросов
            if duration > 1.0:  # > 1 секунды
                logger.warning(
                    f"🐌 Slow request: {request.method} {request.url.path} "
                    f"took {duration:.2f}s"
                )
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            self.monitor.record_request(
                endpoint=request.url.path,
                duration=duration,
                status_code=500
            )
            raise


@asynccontextmanager
async def measure_time(operation: str):
    """
    Context manager для измерения времени выполнения
    
    Usage:
        async with measure_time("database_query"):
            result = await db.execute(query)
    """
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(f"⏱️ {operation} took {duration:.4f}s")


def measure_execution_time(func):
    """
    Декоратор для измерения времени выполнения функции
    
    Usage:
        @measure_execution_time
        async def slow_function():
            ...
    """
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start
            if duration > 0.5:  # Логируем если > 500ms
                logger.warning(
                    f"⏱️ {func.__name__} took {duration:.4f}s"
                )
    
    return wrapper


# Глобальный монитор
performance_monitor = PerformanceMonitor()
