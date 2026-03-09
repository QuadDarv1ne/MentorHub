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
        
        # Статистика кеша
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        
        # Размеры кеша
        self.cache_sizes = {
            "memory": 0,
            "redis": 0
        }

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
                else:
                    self.stats["misses"] += 1
            else:
                if key in self.memory_cache:
                    self.stats["hits"] += 1
                    return self.memory_cache.get(key)
                else:
                    self.stats["misses"] += 1
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats["errors"] += 1

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = 300):  # 5 минут по умолчанию
        """Сохранение значения в кеш"""
        try:
            serialized_value = json.dumps(value)
            value_size = len(serialized_value)
            
            if self.use_redis:
                await self.redis.setex(key, ttl or 3600, serialized_value)  # 1 час максимум
                self.cache_sizes["redis"] += value_size
            else:
                # В памяти без TTL (ограничение)
                if len(self.memory_cache) > 1000:
                    # Очистка половины кеша при переполнении
                    keys_to_delete = list(self.memory_cache.keys())[:500]
                    for k in keys_to_delete:
                        # Вычитаем размер удаляемого значения
                        if k in self.memory_cache:
                            old_value = json.dumps(self.memory_cache[k])
                            self.cache_sizes["memory"] -= len(old_value)
                        del self.memory_cache[k]

                self.memory_cache[key] = value
                self.cache_sizes["memory"] += value_size
                
            self.stats["sets"] += 1

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.stats["errors"] += 1

    async def delete(self, key: str):
        """Удаление из кеша"""
        try:
            if self.use_redis:
                # Получаем размер удаляемого значения для статистики
                value = await self.redis.get(key)
                if value:
                    self.cache_sizes["redis"] -= len(value)
                await self.redis.delete(key)
            else:
                # Получаем размер удаляемого значения для статистики
                if key in self.memory_cache:
                    old_value = json.dumps(self.memory_cache[key])
                    self.cache_sizes["memory"] -= len(old_value)
                self.memory_cache.pop(key, None)
            self.stats["deletes"] += 1
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            self.stats["errors"] += 1

    async def clear(self, pattern: str = "*"):
        """Очистка кеша по паттерну"""
        try:
            if self.use_redis:
                keys = await self.redis.keys(pattern)
                if keys:
                    # Сбрасываем статистику размеров
                    self.cache_sizes["redis"] = 0
                    await self.redis.delete(*keys)
            else:
                if pattern == "*":
                    # Сбрасываем статистику размеров
                    self.cache_sizes["memory"] = 0
                    self.memory_cache.clear()
                else:
                    # Простая очистка по префиксу
                    prefix = pattern.replace("*", "")
                    keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(prefix)]
                    for k in keys_to_delete:
                        # Вычитаем размер удаляемого значения
                        if k in self.memory_cache:
                            old_value = json.dumps(self.memory_cache[k])
                            self.cache_sizes["memory"] -= len(old_value)
                        del self.memory_cache[k]

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            self.stats["errors"] += 1

    def generate_key(self, *args, **kwargs) -> str:
        """Генерация ключа кеша из параметров"""
        key_data = f"{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_stats(self) -> dict:
        """Получение статистики кеша"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "stats": self.stats.copy(),
            "hit_rate": round(hit_rate, 2),
            "cache_sizes": self.cache_sizes.copy(),
            "total_requests": total_requests
        }

    def reset_stats(self):
        """Сброс статистики кеша"""
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }


# Глобальный экземпляр
cache_manager: Optional[CacheManager] = None


def init_cache(redis_client: Optional[Redis] = None):
    """Инициализация кеш-менеджера"""
    global cache_manager
    cache_manager = CacheManager(redis_client)
    return cache_manager


def cached(ttl: int = 300, key_prefix: str = "", skip_auth: bool = False, cache_none: bool = False, invalidate_on_error: bool = False):
    """
    Декоратор для кеширования результатов функций

    Args:
        ttl: Время жизни кеша в секундах
        key_prefix: Префикс для ключа кеша
        skip_auth: Не учитывать user_id в ключе
        cache_none: Кешировать None значения
        invalidate_on_error: Инвалидировать кеш при ошибках

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
                return cached_result

            # Выполнение функции
            try:
                result = await func(*args, **kwargs)

                # Сохранение в кеш
                if result is not None or cache_none:
                    await cache_manager.set(cache_key, result, ttl)

                return result
            except Exception as e:
                if invalidate_on_error:
                    await cache_manager.delete(cache_key)
                raise

        return wrapper

    return decorator


async def invalidate_cache(pattern: str):
    """Инвалидация кеша по паттерну"""
    if cache_manager:
        await cache_manager.clear(pattern)
        logger.info(f"🗑️ Cache invalidated: {pattern}")


def get_cache_stats() -> dict:
    """Получение статистики кеша"""
    if cache_manager:
        return cache_manager.get_stats()
    return {}


def reset_cache_stats():
    """Сброс статистики кеша"""
    if cache_manager:
        cache_manager.reset_stats()
        logger.info("📊 Cache stats reset")


# Предустановленные TTL для различных типов данных
CACHE_TTL = {
    "user": 600,  # 10 минут
    "mentor": 900,  # 15 минут
    "course": 1800,  # 30 минут
    "review": 300,  # 5 минут
    "stats": 60,  # 1 минута
    "session": 120,  # 2 минуты
    "list": 180,  # 3 минуты (списки)
    "achievement": 300,  # 5 минут
    "payment": 600,  # 10 минут
    "message": 120,  # 2 минуты
}

# Конфигурация кеша
CACHE_CONFIG = {
    "max_memory_items": 1000,
    "cleanup_threshold": 500,
    "default_ttl": 300,
    "max_ttl": 3600
}
