"""
Security Middleware

Main security middleware for protecting against various attacks.
Uses modular security components for detection and sanitization.
"""

import logging
import os
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Callable, Dict, List, Optional
from urllib.parse import unquote_plus

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.middleware.security_patterns import SecurityPatterns
from app.middleware.security_detectors import SecurityDetector
from app.utils.antiphishing import AntiPhishingValidator

logger = logging.getLogger(__name__)


# Constants for security middleware
DEFAULT_RATE_LIMIT_REQUESTS = 100
DEFAULT_RATE_LIMIT_WINDOW = 60  # seconds
DEFAULT_MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_HSTS_MAX_AGE = 31536000  # 1 year in seconds
DEFAULT_TRUNCATE_LOG_LENGTH = 100  # characters for logging


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware for protection against various attacks.
    
    Protects against:
    - SQL Injection
    - XSS (Cross-Site Scripting)
    - Path Traversal
    - Command Injection
    - Clickjacking
    - CSRF (Cross-Site Request Forgery)
    - Malicious User-Agents
    - Phishing attempts
    """

    def __init__(
        self,
        app,
        rate_limit_requests: int = DEFAULT_RATE_LIMIT_REQUESTS,
        rate_limit_window: int = DEFAULT_RATE_LIMIT_WINDOW,
        max_body_size: int = DEFAULT_MAX_BODY_SIZE,
    ):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.request_counts: Dict[str, List[datetime]] = defaultdict(list)
        self.max_body_size = max_body_size
        
        # Initialize security detector
        self.detector = SecurityDetector(
            truncate_log_length=DEFAULT_TRUNCATE_LOG_LENGTH
        )

    async def dispatch(self, request: Request, call_next: Callable):
        """Process each request through security checks."""
        
        # Skip security checks for documentation and health endpoints
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health", "/metrics"]:
            return await call_next(request)

        # Rate limiting check
        await self._check_rate_limit(request)

        # Check request size
        await self._check_request_size(request)

        # Check query parameters
        self._check_query_params(request)

        # Check request body for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            await self._check_request_body(request)

        # Check headers
        self._check_headers(request)

        # Process request
        response = await call_next(request)

        # Add security headers
        response = self._add_security_headers(response)

        return response

    async def _check_rate_limit(self, request: Request):
        """Check rate limiting."""
        client_ip = request.client.host
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self.rate_limit_window)

        # Clean old requests
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if req_time > window_start
        ]

        # Check limit
        if len(self.request_counts[client_ip]) >= self.rate_limit_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )

        # Record request
        self.request_counts[client_ip].append(now)

    async def _check_request_size(self, request: Request):
        """Check request body size."""
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            logger.warning(f"Request body too large: {content_length} bytes")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request body too large"
            )

    def _check_query_params(self, request: Request):
        """Check query parameters for attacks."""
        query_string = str(request.query_params)
        
        if self.detector.detect_path_traversal(query_string):
            try:
                from app.utils.prometheus import record_security_incident
                record_security_incident("path_traversal", request.url.path)
            except Exception as e:
                logger.debug(f"Failed to record security metric: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Path traversal attempt detected"
            )

    async def _check_request_body(self, request: Request):
        """Check request body for attacks."""
        try:
            body = await request.body()
            body_str = body.decode("utf-8", errors="ignore")

            # Check JSON body
            if body_str.strip().startswith(("{", "[")):
                try:
                    json_body = json.loads(body_str)
                    self.detector.check_json_values(json_body)
                except json.JSONDecodeError:
                    pass  # Not valid JSON, check as plain text

            # Check for SQL injection
            if self.detector.detect_sql_injection(body_str):
                try:
                    from app.utils.prometheus import record_security_incident
                    record_security_incident("sql_injection", request.url.path)
                except Exception as e:
                    logger.debug(f"Failed to record security metric: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SQL injection attempt detected"
                )

            # Check for XSS
            if self.detector.detect_xss(body_str):
                try:
                    from app.utils.prometheus import record_security_incident
                    record_security_incident("xss", request.url.path)
                except Exception as e:
                    logger.debug(f"Failed to record security metric: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="XSS attempt detected"
                )

            # Check for command injection
            if self.detector.detect_command_injection(body_str):
                try:
                    from app.utils.prometheus import record_security_incident
                    record_security_incident("command_injection", request.url.path)
                except Exception as e:
                    logger.debug(f"Failed to record security metric: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Command injection attempt detected"
                )

        except UnicodeDecodeError:
            logger.debug("UnicodeDecodeError in request body, skipping binary data")

    def _check_headers(self, request: Request):
        """Check request headers."""
        # Check User-Agent
        user_agent = request.headers.get("User-Agent", "")
        self.detector.check_user_agent(user_agent, request.url.path)

        # Check Referer
        referer = request.headers.get("Referer", "")
        self.detector.check_referer(referer)

    def _add_security_headers(self, response) -> JSONResponse:
        """Add security headers to response."""
        # XSS Protection
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'; "
            "upgrade-insecure-requests;"
        )

        # HSTS
        response.headers["Strict-Transport-Security"] = (
            f"max-age={DEFAULT_HSTS_MAX_AGE}; includeSubDomains; preload"
        )

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "fullscreen=(self), payment=(), usb=()"
        )

        return response
