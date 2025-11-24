"""
Rate Limiting Middleware
Защита от DDoS атак и злоупотреблений API
"""

from typing import Callable
import time
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis

from app.config import settings


class RateLimiter:
    """Rate limiter with Redis backend"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.memory_store = defaultdict(list)  # Fallback if Redis unavailable
        
    async def is_rate_limited(
        self, 
        key: str, 
        max_requests: int = 100, 
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request should be rate limited
        
        Args:
            key: Unique identifier (IP address, user ID, etc.)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            True if rate limit exceeded, False otherwise
        """
        try:
            # Try Redis first
            current_time = time.time()
            redis_key = f"rate_limit:{key}"
            
            # Get current count
            pipe = self.redis.pipeline()
            pipe.zadd(redis_key, {str(current_time): current_time})
            pipe.zremrangebyscore(redis_key, 0, current_time - window_seconds)
            pipe.zcard(redis_key)
            pipe.expire(redis_key, window_seconds)
            
            results = await pipe.execute()
            request_count = results[2]
            
            return request_count > max_requests
            
        except Exception:
            # Fallback to memory store
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=window_seconds)
            
            # Clean old entries
            self.memory_store[key] = [
                req_time for req_time in self.memory_store[key]
                if req_time > window_start
            ]
            
            # Add current request
            self.memory_store[key].append(current_time)
            
            return len(self.memory_store[key]) > max_requests
    
    async def get_remaining_requests(
        self, 
        key: str, 
        max_requests: int = 100, 
        window_seconds: int = 60
    ) -> int:
        """Get number of remaining requests in current window"""
        try:
            current_time = time.time()
            redis_key = f"rate_limit:{key}"
            
            # Clean old entries and count
            await self.redis.zremrangebyscore(
                redis_key, 
                0, 
                current_time - window_seconds
            )
            request_count = await self.redis.zcard(redis_key)
            
            return max(0, max_requests - request_count)
            
        except Exception:
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=window_seconds)
            
            self.memory_store[key] = [
                req_time for req_time in self.memory_store[key]
                if req_time > window_start
            ]
            
            return max(0, max_requests - len(self.memory_store[key]))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware для ограничения частоты запросов
    
    Лимиты:
    - Анонимные пользователи: 100 запросов/минуту
    - Авторизованные: 1000 запросов/минуту
    - Auth endpoints: 10 попыток/минуту
    """
    
    def __init__(self, app, redis_client: Redis):
        super().__init__(app)
        self.limiter = RateLimiter(redis_client)
        
        # Rate limit configurations
        self.configs = {
            "default": {"max_requests": 100, "window": 60},
            "authenticated": {"max_requests": 1000, "window": 60},
            "auth": {"max_requests": 10, "window": 60},
            "strict": {"max_requests": 5, "window": 60},
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_rate_limit_config(self, path: str, user_id: str = None) -> dict:
        """Get rate limit configuration for endpoint"""
        # Auth endpoints are strictly limited
        if path.startswith("/api/v1/auth/login") or path.startswith("/api/v1/auth/register"):
            return self.configs["auth"]
        
        # Password reset is very strict
        if "password" in path or "reset" in path:
            return self.configs["strict"]
        
        # Authenticated users get higher limits
        if user_id:
            return self.configs["authenticated"]
        
        # Default for anonymous users
        return self.configs["default"]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ready", "/api/v1/health/detailed"]:
            return await call_next(request)
        
        # Get client identifier
        client_ip = self._get_client_ip(request)
        user_id = request.state.user.id if hasattr(request.state, "user") else None
        
        # Use user_id for authenticated requests, IP for anonymous
        rate_limit_key = f"user:{user_id}" if user_id else f"ip:{client_ip}"
        
        # Get appropriate rate limit config
        config = self._get_rate_limit_config(request.url.path, user_id)
        
        # Check rate limit
        is_limited = await self.limiter.is_rate_limited(
            rate_limit_key,
            max_requests=config["max_requests"],
            window_seconds=config["window"]
        )
        
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Maximum {config['max_requests']} requests per {config['window']} seconds.",
                    "retry_after": config["window"]
                }
            )
        
        # Get remaining requests for headers
        remaining = await self.limiter.get_remaining_requests(
            rate_limit_key,
            max_requests=config["max_requests"],
            window_seconds=config["window"]
        )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(config["max_requests"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + config["window"])
        
        return response


def create_rate_limiter(redis_client: Redis) -> RateLimiter:
    """Factory function to create rate limiter instance"""
    return RateLimiter(redis_client)
