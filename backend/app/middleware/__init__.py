"""
Middleware Module

Centralized middleware registration and utilities.
Consolidated middleware to avoid duplication.
"""

from .rate_limiter_unified import (
    UnifiedRateLimitMiddleware,
    RateLimiter,
    create_rate_limiter,
    # Backward compatibility
    RateLimitMiddleware,
    AdvancedRateLimitMiddleware,
)
from .security_advanced import SecurityMiddleware
from .request_id import RequestIDMiddleware
from .request_logging import RequestLoggingMiddleware
from .setup import register_middleware

__all__ = [
    # Rate limiting (unified)
    "UnifiedRateLimitMiddleware",
    "RateLimiter",
    "create_rate_limiter",
    
    # Backward compatibility aliases
    "RateLimitMiddleware",
    "AdvancedRateLimitMiddleware",

    # Security
    "SecurityMiddleware",

    # Request handling
    "RequestIDMiddleware",
    "RequestLoggingMiddleware",

    # Setup utilities
    "register_middleware",
]
