"""
Cache service using in-memory cache or Redis
"""

import json
import logging
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class CacheEntry:
    """Wrapper for cache entries with expiration time"""
    value: Any
    expires_at: float  # Unix timestamp when the entry expires


class CacheService:
    """Simple cache service with optional Redis backend"""

    def __init__(self):
        self.redis_client = None
        self.memory_cache: dict[str, CacheEntry] = {}
        self._redis_connected = False

        # Try to connect to Redis if available
        if REDIS_AVAILABLE:
            try:
                from app.config import settings

                redis_url = getattr(settings, "REDIS_URL", None)

                if redis_url:
                    # Проверяем, что URL не содержит localhost или docker hostname
                    if any(host in redis_url for host in ["localhost", "127.0.0.1", "redis:"]):
                        # В cloud environment эти hostname не будут работать
                        import os
                        if not any(os.environ.get(key) for key in ["RENDER", "RAILWAY", "FLY", "KUBERNETES_SERVICE_HOST"]):
                            logger.debug(f"Redis URL uses local hostname: {redis_url}")

                    self.redis_client = redis.from_url(redis_url, decode_responses=True)
                    self.redis_client.ping()
                    self._redis_connected = True
                    logger.info("✅ Redis cache connected")
                else:
                    logger.debug("REDIS_URL not configured, using memory cache")
            except Exception as e:
                # Логируем только на уровне DEBUG, чтобы не спамить в production
                logger.debug(f"Redis connection failed: {e}")
                logger.info("ℹ️ Using memory cache (Redis not available)")
                self.redis_client = None

    def get(self, key: str) -> Any | None:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                entry = self.memory_cache.get(key)
                if entry:
                    # Проверяем, не истёк ли TTL
                    if time.time() < entry.expires_at:
                        return entry.value
                    else:
                        # Удаляем протухшую запись
                        del self.memory_cache[key]
                        logger.debug(f"Cache entry expired: {key}")
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")

        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
        """
        try:
            if self.redis_client:
                serialized = json.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
            else:
                expires_at = time.time() + ttl
                self.memory_cache[key] = CacheEntry(value=value, expires_at=expires_at)

            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)

            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache and is not expired"""
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                entry = self.memory_cache.get(key)
                if entry:
                    if time.time() < entry.expires_at:
                        return True
                    else:
                        # Удаляем протухшую запись
                        del self.memory_cache[key]
                        logger.debug(f"Cache entry expired (exists check): {key}")
                return False
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    def cleanup_expired(self) -> int:
        """Remove all expired entries from memory cache. Returns count of removed entries."""
        if self.redis_client:
            return 0  # Redis handles TTL automatically

        now = time.time()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if now >= entry.expires_at
        ]

        for key in expired_keys:
            del self.memory_cache[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def clear(self) -> bool:
        """Clear all cache"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()

            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False


# Singleton instance
cache_service = CacheService()


# Decorator for caching function results
def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results

    Usage:
        @cached(ttl=600, key_prefix="user")
        async def get_user(user_id: int):
            return db.query(User).filter(User.id == user_id).first()
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
