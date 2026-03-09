"""
Advanced caching utilities
Продвинутое кэширование с поддержкой Redis и декораторов
"""

import logging
import json
import hashlib
from typing import Optional, Callable, Any
from functools import wraps
from datetime import timedelta

logger = logging.getLogger(__name__)

# Global cache instance (будет установлен при инициализации)
cache_backend = None


class CacheBackend:
    """Абстрактный backend для кэширования"""
    
    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError
    
    async def set(self, key: str, value: str, ttl: int):
        raise NotImplementedError
    
    async def delete(self, key: str):
        raise NotImplementedError
    
    async def clear(self, pattern: str = "*"):
        raise NotImplementedError


class RedisCache(CacheBackend):
    """Redis кэш backend"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[str]:
        try:
            value = await self.redis.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int):
        try:
            await self.redis.setex(key, ttl, value)
        except Exception as e:
            logger.warning(f"Redis set error: {e}")
    
    async def delete(self, key: str):
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")
    
    async def clear(self, pattern: str = "*"):
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Redis clear error: {e}")


class MemoryCache(CacheBackend):
    """In-memory кэш backend (fallback)"""
    
    def __init__(self):
        self._cache = {}
        self._ttl = {}
    
    async def get(self, key: str) -> Optional[str]:
        import time
        if key in self._cache:
            # Проверяем TTL
            if key in self._ttl and time.time() > self._ttl[key]:
                del self._cache[key]
                del self._ttl[key]
                return None
            return self._cache[key]
        return None
    
    async def set(self, key: str, value: str, ttl: int):
        import time
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl
    
    async def delete(self, key: str):
        self._cache.pop(key, None)
        self._ttl.pop(key, None)
    
    async def clear(self, pattern: str = "*"):
        if pattern == "*":
            self._cache.clear()
            self._ttl.clear()
        else:
            # Простая фильтрация по началу ключа
            prefix = pattern.rstrip("*")
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                self._cache.pop(key, None)
                self._ttl.pop(key, None)


def init_cache_backend(redis_client=None):
    """
    Инициализация кэш backend
    
    Args:
        redis_client: Redis клиент (опционально)
    """
    global cache_backend
    
    if redis_client:
        cache_backend = RedisCache(redis_client)
        logger.info("✅ Redis cache backend initialized")
    else:
        cache_backend = MemoryCache()
        logger.info("⚠️ Memory cache backend initialized (fallback)")


def cache_key(*args, **kwargs) -> str:
    """
    Генерация ключа кэша из аргументов
    
    Args:
        *args: Позиционные аргументы
        **kwargs: Именованные аргументы
        
    Returns:
        str: Хэш ключ
    """
    # Сериализуем аргументы
    key_data = json.dumps({
        "args": args,
        "kwargs": sorted(kwargs.items())
    }, sort_keys=True, default=str)
    
    # Создаем хэш
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_response(
    ttl: int = 300,
    key_prefix: str = "api",
    include_user: bool = False
):
    """
    Декоратор для кэширования ответов API
    
    Args:
        ttl: Time to live в секундах (по умолчанию 5 минут)
        key_prefix: Префикс ключа кэша
        include_user: Включать ли user_id в ключ кэша
        
    Example:
        @router.get("/stats")
        @cache_response(ttl=600, key_prefix="stats")
        async def get_stats():
            return expensive_calculation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Если кэш не инициализирован, просто вызываем функцию
            if cache_backend is None:
                return await func(*args, **kwargs)
            
            # Генерируем ключ кэша
            cache_key_parts = [key_prefix, func.__name__]
            
            # Добавляем user_id если нужно
            if include_user and 'current_user' in kwargs:
                user = kwargs['current_user']
                cache_key_parts.append(f"user_{user.id}")
            
            # Добавляем хэш аргументов
            args_hash = cache_key(
                *[arg for arg in args if not hasattr(arg, '__dict__')],
                **{k: v for k, v in kwargs.items() if k != 'current_user' and k != 'db'}
            )
            cache_key_parts.append(args_hash)
            
            full_cache_key = ":".join(cache_key_parts)
            
            # Пытаемся получить из кэша
            try:
                cached_value = await cache_backend.get(full_cache_key)
                if cached_value:
                    logger.debug(f"✅ Cache hit: {full_cache_key}")
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Cache get error: {e}")
            
            # Вызываем функцию
            logger.debug(f"❌ Cache miss: {full_cache_key}")
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            try:
                await cache_backend.set(
                    full_cache_key,
                    json.dumps(result, default=str),
                    ttl
                )
            except Exception as e:
                logger.warning(f"Cache set error: {e}")
            
            return result
        
        return wrapper
    return decorator


async def invalidate_cache(pattern: str):
    """
    Инвалидация кэша по паттерну
    
    Args:
        pattern: Паттерн ключей для удаления (например "stats:*")
    """
    if cache_backend:
        try:
            await cache_backend.clear(pattern)
            logger.info(f"🗑️ Cache invalidated: {pattern}")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")


async def get_cached(key: str) -> Optional[Any]:
    """
    Получить значение из кэша
    
    Args:
        key: Ключ кэша
        
    Returns:
        Значение из кэша или None
    """
    if cache_backend:
        try:
            value = await cache_backend.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    return None


async def set_cached(key: str, value: Any, ttl: int = 300):
    """
    Сохранить значение в кэш
    
    Args:
        key: Ключ кэша
        value: Значение для сохранения
        ttl: Time to live в секундах
    """
    if cache_backend:
        try:
            await cache_backend.set(
                key,
                json.dumps(value, default=str),
                ttl
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
