"""
API rate limiting middleware
"""
import logging
from typing import Dict
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse
    
    Implements token bucket algorithm:
    - Each IP gets a bucket with max_requests tokens
    - Tokens refill at rate of 1 per refill_period seconds
    - Requests consume 1 token
    """
    
    def __init__(
        self,
        app,
        max_requests: int = 100,
        time_window: int = 60,  # seconds
        exclude_paths: list = None
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.exclude_paths = exclude_paths or ['/health', '/ready', '/docs', '/redoc']
        
        # Storage: {ip: {'count': int, 'reset_time': datetime}}
        self.request_counts: Dict[str, Dict] = defaultdict(dict)
        
        logger.info(f"✅ Rate limiting enabled: {max_requests} requests per {time_window}s")
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(self.time_window)}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        bucket = self.request_counts[client_ip]
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.max_requests - bucket.get('count', 0))
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(bucket.get('reset_time', datetime.now()).timestamp())
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for X-Forwarded-For header (when behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Check if request is within rate limit
        
        Returns:
            bool: True if request is allowed, False if rate limit exceeded
        """
        now = datetime.now()
        bucket = self.request_counts[client_ip]
        
        # Initialize or reset bucket if time window has passed
        if 'reset_time' not in bucket or now >= bucket['reset_time']:
            bucket['count'] = 0
            bucket['reset_time'] = now + timedelta(seconds=self.time_window)
        
        # Check if under limit
        if bucket['count'] >= self.max_requests:
            return False
        
        # Increment counter
        bucket['count'] += 1
        
        return True
    
    def clear_ip(self, client_ip: str):
        """Clear rate limit for specific IP (admin function)"""
        if client_ip in self.request_counts:
            del self.request_counts[client_ip]
            logger.info(f"Rate limit cleared for IP: {client_ip}")
    
    def clear_all(self):
        """Clear all rate limits (admin function)"""
        self.request_counts.clear()
        logger.info("All rate limits cleared")
