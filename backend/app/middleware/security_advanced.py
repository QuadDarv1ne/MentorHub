"""
Security Middleware

Main security middleware for protecting against various attacks.
Uses modular security components for detection and sanitization.
Rate limiting is handled by UnifiedRateLimitMiddleware (Redis-backed).
"""

import json
import logging
from typing import Callable

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.middleware.security_detectors import SecurityDetector

logger = logging.getLogger(__name__)


# Constants for security middleware
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
    - Request size abuse
    - Malicious User-Agents
    - Adds security response headers (CSP, HSTS, etc.)
    """

    def __init__(
        self,
        app,
        max_body_size: int = DEFAULT_MAX_BODY_SIZE,
    ):
        super().__init__(app)
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
        return self._add_security_headers(response)

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
