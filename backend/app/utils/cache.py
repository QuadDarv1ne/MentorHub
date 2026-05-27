"""
Система кеширования для MentorHub
Поддержка Redis и in-memory fallback

Type hints added for better IDE support and type checking.
"""

from __future__ import annotations

import hashlib
import json
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

try:
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.constants import (
    CACHE_TTL_ANALYTICS,
    CACHE_TTL_COURSE,
    CACHE_TTL_DEFAULT,
    CACHE_TTL_MENTOR,
    CACHE_TTL_REVIEW,
    CACHE_TTL_STATS,
    CACHE_TTL_SUBSCRIPTION,
    CACHE_TTL_USER,
    MAX_CACHE_TTL,
    MAX_MEMORY_CACHE_ITEMS,
)

logger = logging.getLogger(__name__)

# Константы для кеширования (экспорт из constants.py)
DEFAULT_CACHE_TTL = CACHE_TTL_DEFAULT  # 5 минут
DEFAULT_CACHE_EXPIRATION = CACHE_TTL_SUBSCRIPTION  # 1 час
MEMORY_CACHE_CLEANUP_COUNT = 500


class CacheManager:
    """Менеджер кеширования с поддержкой Redis и памяти"""

    def __init__(self, redis_client: Optional[Redis] = None) -> None:
        self.redis = redis_client
        self.memory_cache: Dict[str, Any] = {}
        self.use_redis = redis_client is not None
        self.stats: Dict[str, int] = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "errors": 0}
        self.cache_sizes: Dict[str, int] = {"memory": 0, "redis": 0}

        if self.use_redis:
            logger.info("✅ Cache: используется Redis")
        else:
            logger.warning("⚠️ Cache: используется память (ограниченная)")

    async def get(self, key: str) -> Optional[Any]:
        """Получение значения из кеша"""
        try:
            if self.use_redis:
                value = await self.redis.get(key)
                if value:
                    self.stats["hits"] += 1
                    return json.loads(value)
                self.stats["misses"] += 1
            else:
                if key in self.memory_cache:
                    self.stats["hits"] += 1
                    return self.memory_cache.get(key)
                self.stats["misses"] += 1
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats["errors"] += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = DEFAULT_CACHE_TTL) -> None:
        """Сохранение значения в кеш"""
        try:
            serialized_value = json.dumps(value)
            value_size = len(serialized_value)

            if self.use_redis:
                await self.redis.setex(key, ttl or DEFAULT_CACHE_EXPIRATION, serialized_value)
                self.cache_sizes["redis"] += value_size
            else:
                if len(self.memory_cache) > MAX_MEMORY_CACHE_ITEMS:
                    keys_to_delete: List[str] = list(self.memory_cache.keys())[:MEMORY_CACHE_CLEANUP_COUNT]
                    for k in keys_to_delete:
                        if k in self.memory_cache:
                            self.cache_sizes["memory"] -= len(json.dumps(self.memory_cache[k]))
                        del self.memory_cache[k]
                self.memory_cache[key] = value
                self.cache_sizes["memory"] += value_size
            self.stats["sets"] += 1
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.stats["errors"] += 1

    async def delete(self, key: str) -> None:
        """Удаление из кеша"""
        try:
            if self.use_redis:
                value = await self.redis.get(key)
                if value:
                    self.cache_sizes["redis"] -= len(value)
                await self.redis.delete(key)
            else:
                if key in self.memory_cache:
                    self.cache_sizes["memory"] -= len(json.dumps(self.memory_cache[key]))
                self.memory_cache.pop(key, None)
            self.stats["deletes"] += 1
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            self.stats["errors"] += 1

    async def clear(self, pattern: str = "*") -> None:
        """Очистка кеша по паттерну"""
        try:
            if self.use_redis:
                keys = await self.redis.keys(pattern)
                if keys:
                    self.cache_sizes["redis"] = 0
                    await self.redis.delete(*keys)
            else:
                if pattern == "*":
                    self.cache_sizes["memory"] = 0
                    self.memory_cache.clear()
                else:
                    prefix = pattern.replace("*", "")
                    keys_to_delete: List[str] = [k for k in self.memory_cache.keys() if k.startswith(prefix)]
                    for k in keys_to_delete:
                        if k in self.memory_cache:
                            self.cache_sizes["memory"] -= len(json.dumps(self.memory_cache[k]))
                        del self.memory_cache[k]
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            self.stats["errors"] += 1

    def generate_key(self, *args: Any, **kwargs: Any) -> str:
        """Генерация ключа кеша из параметров"""
        key_data = f"{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кеша"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        return {
            "stats": self.stats.copy(),
            "hit_rate": round(hit_rate, 2),
            "cache_sizes": self.cache_sizes.copy(),
            "total_requests": total_requests
        }

    def reset_stats(self) -> None:
        """Сброс статистики кеша"""
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "errors": 0}


# Глобальный экземпляр
cache_manager: Optional[CacheManager] = None


def init_cache(redis_client: Optional[Redis] = None) -> CacheManager:
    """Инициализация кеш-менеджера"""
    global cache_manager
    cache_manager = CacheManager(redis_client)
    return cache_manager


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    skip_auth: bool = False,
    cache_none: bool = False,
    invalidate_on_error: bool = False
) -> Callable:
    """
    Декоратор для кеширования результатов функций

    Args:
        ttl: Время жизни кеша в секундах
        key_prefix: Префикс для ключа кеша
        skip_auth: Не учитывать user_id в ключе
        cache_none: Кешировать None значения
        invalidate_on_error: Инвалидировать кеш при ошибках
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not cache_manager:
                return await func(*args, **kwargs)

            cache_key = f"{key_prefix}:{func.__name__}:"
            key_parts: List[str] = []

            for arg in args:
                if hasattr(arg, "id"):
                    key_parts.append(f"{arg.__class__.__name__}_{arg.id}")
                elif not isinstance(arg, (dict, list)):
                    key_parts.append(str(arg))

            for k, v in sorted(kwargs.items()):
                if k == "current_user" and skip_auth:
                    continue
                if hasattr(v, "id"):
                    key_parts.append(f"{k}_{v.id}")
                elif not isinstance(v, (dict, list)):
                    key_parts.append(f"{k}_{v}")

            cache_key += "_".join(key_parts)

            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            try:
                result = await func(*args, **kwargs)
                if result is not None or cache_none:
                    await cache_manager.set(cache_key, result, ttl)
                return result
            except Exception:
                if invalidate_on_error:
                    await cache_manager.delete(cache_key)
                raise

        return wrapper
    return decorator


async def invalidate_cache(pattern: str) -> None:
    """Инвалидация кеша по паттерну"""
    if cache_manager:
        await cache_manager.clear(pattern)
        logger.info(f"🗑️ Cache invalidated: {pattern}")


def get_cache_stats() -> Dict[str, Any]:
    """Получение статистики кеша"""
    return cache_manager.get_stats() if cache_manager else {}


def reset_cache_stats() -> None:
    """Сброс статистики кеша"""
    if cache_manager:
        cache_manager.reset_stats()
        logger.info("📊 Cache stats reset")


CACHE_TTL = {
    "user": CACHE_TTL_USER,
    "mentor": CACHE_TTL_MENTOR,
    "course": CACHE_TTL_COURSE,
    "review": CACHE_TTL_REVIEW,
    "stats": CACHE_TTL_STATS,
    "session": 120,
    "list": 180,
    "achievement": CACHE_TTL_REVIEW,
    "payment": CACHE_TTL_ANALYTICS,
    "message": 120,
    "analytics": CACHE_TTL_ANALYTICS,
    "subscription": CACHE_TTL_SUBSCRIPTION,
}

CACHE_CONFIG = {
    "max_memory_items": MAX_MEMORY_CACHE_ITEMS,
    "cleanup_threshold": MEMORY_CACHE_CLEANUP_COUNT,
    "default_ttl": CACHE_TTL_DEFAULT,
    "max_ttl": MAX_CACHE_TTL
}
