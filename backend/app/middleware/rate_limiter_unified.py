"""
Rate Limiting Middleware

Unified rate limiting with Redis backend and per-endpoint configuration.
Replaces both rate_limiter.py and rate_limit_advanced.py

Features:
- Redis-backed rate limiting with automatic memory fallback
- Per-endpoint rate limits
- User-based throttling (authenticated vs anonymous)
- API abuse protection
- Returns proper 429 responses with retry-after headers
"""

import hashlib
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from app.constants import (
    RATE_LIMIT_ANONYMOUS_REQUESTS,
    RATE_LIMIT_AUTHENTICATED_REQUESTS,
    RATE_LIMIT_DEFAULT_REQUESTS,
    RATE_LIMIT_DEFAULT_WINDOW,
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter with Redis backend and automatic memory fallback"""

    def __init__(self, redis_client: Redis | None = None):
        self.redis = redis_client
        self.memory_store: dict[str, list[datetime]] = defaultdict(list)
        self.memory_store_locks: dict[str, datetime] = {}

    async def is_rate_limited(
        self,
        key: str,
        max_requests: int = RATE_LIMIT_DEFAULT_REQUESTS,
        window_seconds: int = RATE_LIMIT_DEFAULT_WINDOW
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
        # Try Redis first if available
        if self.redis:
            try:
                current_time = time.time()
                redis_key = f"rate_limit:{key}"

                # Use Redis pipeline for atomic operations
                pipe = self.redis.pipeline()
                pipe.zadd(redis_key, {str(current_time): current_time})
                pipe.zremrangebyscore(redis_key, 0, current_time - window_seconds)
                pipe.zcard(redis_key)
                pipe.expire(redis_key, window_seconds)

                results = await pipe.execute()
                request_count = results[2]

                if request_count > max_requests:
                    logger.warning(f"Rate limit exceeded for {key}: {request_count}/{max_requests}")
                    return True
                return False

            except Exception as e:
                logger.debug(f"Redis rate limit failed, using memory fallback: {e}")
                self.redis = None

        # Fallback to memory store
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)

        # Clean old entries
        self.memory_store[key] = [
            req_time for req_time in self.memory_store[key]
            if req_time > window_start
        ]

        # Check limit
        if len(self.memory_store[key]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {key} (memory store)")
            return True

        # Record request
        self.memory_store[key].append(now)
        return False


class UnifiedRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Unified rate limiting middleware with per-endpoint configuration.

    Combines basic and advanced rate limiting into single middleware.
    """

    def __init__(
        self,
        app: Any,
        redis_client: Redis | None = None,
        enabled: bool = True,
    ):
        super().__init__(app)
        self.enabled = enabled
        self.rate_limiter = RateLimiter(redis_client)

        # Per-endpoint rate limits (requests per minute)
        self.endpoint_limits: dict[str, dict[str, int]] = {
            # Auth endpoints (strict limits)
            "/api/auth/login": {"anonymous": 5, "authenticated": 10},
            "/api/auth/register": {"anonymous": 3, "authenticated": 5},
            "/api/auth/password-reset": {"anonymous": 3, "authenticated": 5},
            "/api/2fa": {"anonymous": 5, "authenticated": 10},

            # Payment endpoints (very strict)
            "/api/payments": {"anonymous": 10, "authenticated": 30},
            "/api/subscriptions": {"anonymous": 5, "authenticated": 20},

            # Export endpoints (resource-intensive)
            "/api/export": {"anonymous": 5, "authenticated": 15},

            # Analytics endpoints
            "/api/analytics": {"anonymous": 10, "authenticated": 60},

            # General API (default limits)
            "default": {"anonymous": RATE_LIMIT_ANONYMOUS_REQUESTS, "authenticated": RATE_LIMIT_AUTHENTICATED_REQUESTS},
        }

    def _get_client_key(self, request: Request) -> tuple[str, str]:
        """Generate client key based on IP and user ID"""
        # Get IP address (handle proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")

        # Get user ID from auth header (if authenticated)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_hash = hashlib.sha256(auth_header.encode()).hexdigest()[:16]
            client_id = f"user:{token_hash}"
            user_type = "authenticated"
        else:
            client_id = f"ip:{ip}"
            user_type = "anonymous"

        return client_id, user_type

    def _get_endpoint_key(self, path: str) -> str:
        """Match endpoint to configured limits"""
        path_lower = path.lower()

        for endpoint in self.endpoint_limits:
            if endpoint == "default":
                continue
            if path_lower.startswith(endpoint.lower()):
                return endpoint

        return "default"

    def _get_limits_for_endpoint(self, endpoint_key: str, user_type: str) -> tuple[int, int]:
        """Get rate limits for specific endpoint and user type"""
        limits = self.endpoint_limits.get(endpoint_key, self.endpoint_limits["default"])
        max_requests = limits.get(user_type, limits.get("anonymous", RATE_LIMIT_DEFAULT_REQUESTS))
        window = RATE_LIMIT_DEFAULT_WINDOW  # 1 minute

        return max_requests, window

    async def dispatch(self, request: Request, call_next) -> Any:
        """Process each request through rate limiting"""
        if not self.enabled:
            return await call_next(request)

        # Skip rate limiting for documentation and health endpoints
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health", "/metrics"]:
            return await call_next(request)

        # Get client info
        client_key, user_type = self._get_client_key(request)
        endpoint_key = self._get_endpoint_key(request.url.path)

        # Get limits for this endpoint and user type
        max_requests, window = self._get_limits_for_endpoint(endpoint_key, user_type)

        # Check rate limit
        if await self.rate_limiter.is_rate_limited(client_key, max_requests, window):
            logger.warning(
                f"Rate limit exceeded: {client_key} on {endpoint_key} "
                f"({user_type}: {max_requests} req/{window}s)"
            )

            retry_after = window
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests",
                    "retry_after": retry_after,
                    "limit": max_requests,
                    "window": f"{window} seconds",
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Process request
        return await call_next(request)


# Backward compatibility aliases
RateLimitMiddleware = UnifiedRateLimitMiddleware
AdvancedRateLimitMiddleware = UnifiedRateLimitMiddleware


def create_rate_limiter(redis_client: Redis | None = None) -> RateLimiter:
    """Create rate limiter instance"""
    return RateLimiter(redis_client)
