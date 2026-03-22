"""
Advanced Rate Limiting
Расширенное rate limiting с per-endpoint лимитами

Features:
- Per-endpoint rate limits
- User-based throttling (authenticated vs anonymous)
- API abuse protection
- Slow attack prevention
"""

import time
import hashlib
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)


class AdvancedRateLimiter:
    """Advanced rate limiter with per-endpoint configuration"""

    def __init__(self, redis_client: Redis = None):
        self.redis = redis_client
        self.memory_store: Dict[str, list] = {}
        
        # Per-endpoint rate limits (requests per minute)
        self.endpoint_limits = {
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
            "default": {"anonymous": 60, "authenticated": 100},
        }
        
        # Slow attack prevention (requests per second)
        self.slow_attack_limits = {
            "default": {"anonymous": 10, "authenticated": 20}
        }

    def _get_client_key(self, request: Request) -> Tuple[str, str]:
        """Generate client key based on IP and user ID"""
        # Get IP address (handle proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        # Get user ID from auth header (if authenticated)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_hash = hashlib.sha256(auth_header.encode()).hexdigest()[:16]
            client_id = f"user:{token_hash}"
        else:
            client_id = f"ip:{ip}"
        
        return client_id, ip

    def _get_endpoint_key(self, path: str) -> str:
        """Match endpoint to configured limits"""
        path_lower = path.lower()
        
        for endpoint in self.endpoint_limits:
            if endpoint == "default":
                continue
            if path_lower.startswith(endpoint.lower()):
                return endpoint
        
        return "default"

    async def is_rate_limited(
        self,
        client_key: str,
        endpoint_key: str,
        is_authenticated: bool
    ) -> Tuple[bool, int, int]:
        """
        Check if request should be rate limited
        
        Returns:
            (is_limited, retry_after, remaining_requests)
        """
        user_type = "authenticated" if is_authenticated else "anonymous"
        max_requests = self.endpoint_limits.get(endpoint_key, self.endpoint_limits["default"])[user_type]
        window_seconds = 60
        
        current_time = time.time()
        redis_key = f"rate_limit:{endpoint_key}:{client_key}"
        
        if self.redis:
            try:
                pipe = self.redis.pipeline()
                pipe.zadd(redis_key, {f"{current_time}": current_time})
                pipe.zremrangebyscore(redis_key, 0, current_time - window_seconds)
                pipe.zcard(redis_key)
                pipe.expire(redis_key, window_seconds)
                
                results = await pipe.execute()
                request_count = results[2]
                
                remaining = max(0, max_requests - request_count)
                
                if request_count >= max_requests:
                    # Calculate retry-after
                    oldest = await self.redis.zrange(redis_key, 0, 0, withscores=True)
                    if oldest:
                        retry_after = int(oldest[0][1] + window_seconds - current_time) + 1
                    else:
                        retry_after = window_seconds
                    
                    logger.warning(
                        f"Rate limit exceeded: {client_key} on {endpoint_key} "
                        f"({request_count}/{max_requests})"
                    )
                    return True, retry_after, remaining
                
                return False, 0, remaining
                
            except Exception as e:
                logger.error(f"Redis rate limit error: {e}")
                self.redis = None
        
        # Memory fallback
        if client_key not in self.memory_store:
            self.memory_store[client_key] = []
        
        window_start = current_time - window_seconds
        self.memory_store[client_key] = [
            ts for ts in self.memory_store[client_key]
            if ts > window_start
        ]
        
        request_count = len(self.memory_store[client_key])
        remaining = max(0, max_requests - request_count)
        
        if request_count >= max_requests:
            if self.memory_store[client_key]:
                retry_after = int(self.memory_store[client_key][0] + window_seconds - current_time) + 1
            else:
                retry_after = window_seconds
            
            return True, retry_after, remaining
        
        self.memory_store[client_key].append(current_time)
        return False, 0, remaining

    async def check_slow_attack(
        self,
        client_key: str,
        is_authenticated: bool
    ) -> bool:
        """Detect and prevent slow HTTP attacks"""
        max_rps = self.slow_attack_limits["default"]["authenticated" if is_authenticated else "anonymous"]
        window_seconds = 1
        
        current_time = time.time()
        redis_key = f"slow_attack:{client_key}"
        
        if self.redis:
            try:
                pipe = self.redis.pipeline()
                pipe.zadd(redis_key, {f"{current_time}": current_time})
                pipe.zremrangebyscore(redis_key, 0, current_time - window_seconds)
                pipe.zcard(redis_key)
                pipe.expire(redis_key, window_seconds)
                
                results = await pipe.execute()
                request_count = results[2]
                
                if request_count > max_rps:
                    logger.warning(f"Slow attack detected: {client_key} ({request_count} req/s)")
                    return True
                
                return False
            except Exception:
                pass
        
        return False


class AdvancedRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for advanced rate limiting"""

    def __init__(self, app, redis_client: Redis = None):
        super().__init__(app)
        self.limiter = AdvancedRateLimiter(redis_client)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files
        path = request.url.path
        if path in ["/health", "/ready", "/live"] or path.startswith("/static"):
            return await call_next(request)
        
        # Get client info
        client_key, ip = self.limiter._get_client_key(request)
        endpoint_key = self.limiter._get_endpoint_key(path)
        is_authenticated = request.headers.get("Authorization", "").startswith("Bearer ")
        
        # Check slow attack
        if await self.limiter.check_slow_attack(client_key, is_authenticated):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Slow attack detected.",
                headers={"Retry-After": "60"}
            )
        
        # Check rate limit
        is_limited, retry_after, remaining = await self.limiter.is_rate_limited(
            client_key, endpoint_key, is_authenticated
        )
        
        if is_limited:
            logger.warning(
                f"Rate limit: {ip} on {endpoint_key} - retry after {retry_after}s"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )
        
        # Execute request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(
            self.limiter.endpoint_limits.get(endpoint_key, self.endpoint_limits["default"])[
                "authenticated" if is_authenticated else "anonymous"
            ]
        )
        
        return response
