"""
Input Sanitization Utilities

Sanitization functions for preventing various injection attacks.
"""

import re
from typing import Optional


class InputSanitizer:
    """Input sanitizer for security."""

    @staticmethod
    def sanitize_sql(text: str) -> str:
        """Sanitize input to prevent SQL injection."""
        if not text:
            return text

        # Remove dangerous characters
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        sanitized = text
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")

        return sanitized

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML to prevent XSS."""
        if not text:
            return text

        # Replace dangerous HTML characters
        replacements = {
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;",
        }

        sanitized = text
        for char, replacement in replacements.items():
            sanitized = sanitized.replace(char, replacement)

        return sanitized

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations."""
        if not filename:
            return "file"

        # Remove path traversal
        filename = filename.replace("../", "").replace("..\\", "")

        # Allowed characters only
        allowed_chars = re.compile(r"[^a-zA-Z0-9._-]")
        sanitized = allowed_chars.sub("_", filename)

        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]

        return sanitized

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Validate and sanitize email."""
        if not email:
            return ""

        # Simple email validation
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not email_pattern.match(email):
            return ""

        return email.lower().strip()

    @staticmethod
    def sanitize_url(url: str) -> str:
        """Sanitize URL."""
        if not url:
            return ""

        # Allowed protocols
        allowed_protocols = ["http://", "https://"]
        if not any(url.startswith(proto) for proto in allowed_protocols):
            return ""

        # Remove dangerous characters
        dangerous_chars = ["<", ">", '"', "'", "`"]
        sanitized = url
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")

        return sanitized

    @staticmethod
    def sanitize_username(username: str) -> str:
        """Sanitize username."""
        if not username:
            return ""

        # Allow only alphanumeric and underscore
        allowed_chars = re.compile(r"[^a-zA-Z0-9_]")
        sanitized = allowed_chars.sub("", username)

        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]

        return sanitized

    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Sanitize phone number."""
        if not phone:
            return ""

        # Keep only digits and + sign
        allowed_chars = re.compile(r"[^0-9+]")
        sanitized = allowed_chars.sub("", phone)

        return sanitized
