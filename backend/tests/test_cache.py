"""
Тесты кеширования
Тесты для системы кеширования
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.utils.cache import CacheManager, cached, CACHE_TTL, init_cache, get_cache_stats


class TestCacheManager:
    """Тесты менеджера кеширования"""

    def test_cache_manager_init_without_redis(self):
        """Тест инициализации без Redis"""
        cache = CacheManager(redis_client=None)
        
        assert cache.use_redis is False
        assert cache.memory_cache == {}
        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0

    @pytest.mark.asyncio
    async def test_memory_cache_set_get(self):
        """Тест записи/чтения из memory cache"""
        cache = CacheManager(redis_client=None)
        
        await cache.set("test_key", {"data": "value"}, ttl=300)
        result = await cache.get("test_key")
        
        assert result == {"data": "value"}
        assert cache.stats["hits"] == 1
        assert cache.stats["sets"] == 1

    @pytest.mark.asyncio
    async def test_memory_cache_miss(self):
        """Тест отсутствия ключа в кеше"""
        cache = CacheManager(redis_client=None)
        
        result = await cache.get("nonexistent_key")
        
        assert result is None
        assert cache.stats["misses"] == 1

    @pytest.mark.asyncio
    async def test_memory_cache_delete(self):
        """Тест удаления из кеша"""
        cache = CacheManager(redis_client=None)
        
        await cache.set("to_delete", "value", ttl=300)
        await cache.delete("to_delete")
        result = await cache.get("to_delete")
        
        assert result is None
        assert cache.stats["deletes"] == 1

    @pytest.mark.asyncio
    async def test_memory_cache_clear(self):
        """Тест очистки кеша"""
        cache = CacheManager(redis_client=None)
        
        await cache.set("key1", "value1", ttl=300)
        await cache.set("key2", "value2", ttl=300)
        await cache.clear("*")
        
        assert len(cache.memory_cache) == 0
        assert cache.cache_sizes["memory"] == 0

    def test_generate_key(self):
        """Тест генерации ключа"""
        cache = CacheManager(redis_client=None)
        
        key1 = cache.generate_key("arg1", "arg2", kwarg1="value1")
        key2 = cache.generate_key("arg1", "arg2", kwarg1="value1")
        key3 = cache.generate_key("arg1", "arg2", kwarg1="value2")
        
        assert key1 == key2
        assert key1 != key3

    def test_get_stats(self):
        """Тест получения статистики"""
        cache = CacheManager(redis_client=None)
        
        stats = cache.get_stats()
        
        assert "stats" in stats
        assert "hit_rate" in stats
        assert "cache_sizes" in stats
        assert "total_requests" in stats

    def test_reset_stats(self):
        """Тест сброса статистики"""
        cache = CacheManager(redis_client=None)
        
        cache.stats["hits"] = 100
        cache.reset_stats()
        
        assert cache.stats["hits"] == 0


class TestCachedDecorator:
    """Тесты декоратора кеширования"""

    @pytest.mark.asyncio
    async def test_cached_decorator_hits(self):
        """Тест попадания в кеш через декоратор"""
        init_cache(redis_client=None)
        
        call_count = 0
        
        @cached(ttl=300, key_prefix="test")
        async def test_func(value):
            nonlocal call_count
            call_count += 1
            return value * 2
        
        result1 = await test_func(5)
        result2 = await test_func(5)
        
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Функция вызвана только один раз

    @pytest.mark.asyncio
    async def test_cached_decorator_miss(self):
        """Тест промаха кеша через декоратор"""
        init_cache(redis_client=None)
        
        call_count = 0
        
        @cached(ttl=300, key_prefix="test2")
        async def test_func2(value):
            nonlocal call_count
            call_count += 1
            return value + 10
        
        result1 = await test_func2(5)
        result2 = await test_func2(10)  # Другой аргумент
        
        assert result1 == 15
        assert result2 == 20
        assert call_count == 2  # Функция вызвана дважды для разных аргументов


class TestCacheTTL:
    """Тесты конфигурации TTL"""

    def test_cache_ttl_values(self):
        """Тест значений TTL"""
        assert CACHE_TTL["user"] == 600
        assert CACHE_TTL["mentor"] == 900
        assert CACHE_TTL["course"] == 1800
        assert CACHE_TTL["review"] == 300
        assert CACHE_TTL["stats"] == 60

    def test_cache_ttl_all_positive(self):
        """Тест что все TTL положительные"""
        for key, value in CACHE_TTL.items():
            assert value > 0, f"TTL для {key} должен быть положительным"


class TestCacheIntegration:
    """Интеграционные тесты кеширования"""

    @pytest.mark.asyncio
    async def test_cache_with_complex_data(self):
        """Тест кеширования сложных данных"""
        cache = CacheManager(redis_client=None)
        
        complex_data = {
            "users": [
                {"id": 1, "name": "User1"},
                {"id": 2, "name": "User2"},
            ],
            "total": 2,
            "nested": {
                "key": "value"
            }
        }
        
        await cache.set("complex", complex_data, ttl=300)
        result = await cache.get("complex")
        
        assert result == complex_data
        assert len(result["users"]) == 2
        assert result["nested"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_cache_with_none_value(self):
        """Тест кеширования None значения"""
        cache = CacheManager(redis_client=None)
        
        await cache.set("none_key", None, ttl=300)
        result = await cache.get("none_key")
        
        # None не кешируется по умолчанию
        assert result is None
