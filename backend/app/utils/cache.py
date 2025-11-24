"""
Продвинутая система кеширования для MentorHub
Поддержка Redis и in-memory fallback
"""

import json
import logging
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta

try:
    from redis.asyncio import Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Менеджер кеширования с поддержкой Redis и памяти"""

    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis = redis_client
        self.memory_cache = {}  # Fallback кеш
        self.use_redis = redis_client is not None

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
                    return json.loads(value)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = 300):  # 5 минут по умолчанию
        """Сохранение значения в кеш"""
        try:
            if self.use_redis:
                await self.redis.setex(key, ttl or 3600, json.dumps(value))  # 1 час максимум
            else:
                # В памяти без TTL (ограничение)
                if len(self.memory_cache) > 1000:
                    # Очистка половины кеша при переполнении
                    keys_to_delete = list(self.memory_cache.keys())[:500]
                    for k in keys_to_delete:
                        del self.memory_cache[k]

                self.memory_cache[key] = value

        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def delete(self, key: str):
        """Удаление из кеша"""
        try:
            if self.use_redis:
                await self.redis.delete(key)
            else:
                self.memory_cache.pop(key, None)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    async def clear(self, pattern: str = "*"):
        """Очистка кеша по паттерну"""
        try:
            if self.use_redis:
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
            else:
                if pattern == "*":
                    self.memory_cache.clear()
                else:
                    # Простая очистка по префиксу
                    prefix = pattern.replace("*", "")
                    keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(prefix)]
                    for k in keys_to_delete:
                        del self.memory_cache[k]

        except Exception as e:
            logger.error(f"Cache clear error: {e}")

    def generate_key(self, *args, **kwargs) -> str:
        """Генерация ключа кеша из параметров"""
        key_data = f"{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()


# Глобальный экземпляр
cache_manager: Optional[CacheManager] = None


def init_cache(redis_client: Optional[Redis] = None):
    """Инициализация кеш-менеджера"""
    global cache_manager
    cache_manager = CacheManager(redis_client)
    return cache_manager


def cached(ttl: int = 300, key_prefix: str = "", skip_auth: bool = False):
    """
    Декоратор для кеширования результатов функций

    Args:
        ttl: Время жизни кеша в секундах
        key_prefix: Префикс для ключа кеша
        skip_auth: Не учитывать user_id в ключе

    Usage:
        @cached(ttl=600, key_prefix="mentor")
        async def get_mentor(mentor_id: int):
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cache_manager:
                # Кеш не инициализирован - выполняем напрямую
                return await func(*args, **kwargs)

            # Генерация ключа
            cache_key = f"{key_prefix}:{func.__name__}:"

            # Добавление параметров в ключ
            key_parts = []
            for arg in args:
                if hasattr(arg, "id"):  # SQLAlchemy модели
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

            # Попытка получить из кеша
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"🎯 Cache HIT: {cache_key}")
                return cached_result

            # Выполнение функции
            logger.debug(f"❌ Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)

            # Сохранение в кеш
            if result is not None:
                await cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


async def invalidate_cache(pattern: str):
    """Инвалидация кеша по паттерну"""
    if cache_manager:
        await cache_manager.clear(pattern)
        logger.info(f"🗑️ Cache invalidated: {pattern}")


# Предустановленные TTL для различных типов данных
CACHE_TTL = {
    "user": 600,  # 10 минут
    "mentor": 900,  # 15 минут
    "course": 1800,  # 30 минут
    "review": 300,  # 5 минут
    "stats": 60,  # 1 минута
    "session": 120,  # 2 минуты
    "list": 180,  # 3 минуты (списки)
}
