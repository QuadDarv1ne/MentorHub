"""
Security Attack Detectors

Detection logic for various security attacks.
"""

import logging
import re
from typing import Any

from fastapi import HTTPException, status

from app.middleware.security_patterns import SecurityPatterns

logger = logging.getLogger(__name__)


class SecurityDetector:
    """Security attack detector."""

    def __init__(self, truncate_log_length: int = 100):
        self.truncate_log_length = truncate_log_length
        self.sql_patterns = SecurityPatterns.get_compiled_patterns(
            SecurityPatterns.SQL_INJECTION_PATTERNS
        )
        self.xss_patterns = SecurityPatterns.get_compiled_patterns(
            SecurityPatterns.XSS_PATTERNS
        )
        self.path_traversal_patterns = SecurityPatterns.get_compiled_patterns(
            SecurityPatterns.PATH_TRAVERSAL_PATTERNS
        )
        self.command_injection_patterns = SecurityPatterns.get_compiled_patterns(
            SecurityPatterns.COMMAND_INJECTION_PATTERNS
        )

    def detect_sql_injection(self, text: str) -> bool:
        """Detect SQL injection attempts."""
        if not text:
            return False

        text_lower = text.lower()
        for pattern in self.sql_patterns:
            if pattern.search(text_lower):
                logger.warning(
                    f"SQL Injection pattern detected: {pattern.pattern} in text: "
                    f"{text[:self.truncate_log_length]}..."
                )
                return True
        return False

    def detect_xss(self, text: str) -> bool:
        """Detect XSS attempts."""
        if not text:
            return False

        text_lower = text.lower()
        for pattern in self.xss_patterns:
            if pattern.search(text_lower):
                logger.warning(
                    f"XSS pattern detected: {pattern.pattern} in text: "
                    f"{text[:self.truncate_log_length]}..."
                )
                return True
        return False

    def detect_path_traversal(self, text: str) -> bool:
        """Detect path traversal attempts."""
        if not text:
            return False

        for pattern in self.path_traversal_patterns:
            if pattern.search(text, re.IGNORECASE):
                logger.warning(
                    f"Path traversal pattern detected: {pattern.pattern} in text: "
                    f"{text[:self.truncate_log_length]}..."
                )
                return True
        return False

    def detect_command_injection(self, text: str) -> bool:
        """Detect command injection attempts."""
        if not text:
            return False

        for pattern in self.command_injection_patterns:
            if pattern.search(text, re.IGNORECASE):
                logger.warning(
                    f"Command injection pattern detected: {pattern.pattern} in text: "
                    f"{text[:self.truncate_log_length]}..."
                )
                return True
        return False

    def check_json_values(self, obj: Any) -> None:
        """
        Recursively check JSON values for attacks.
        
        Raises:
            HTTPException: If attack is detected
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    if self.detect_sql_injection(value):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"SQL injection attempt in field '{key}'"
                        )
                    if self.detect_xss(value):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"XSS attempt in field '{key}'"
                        )
                    if self.detect_command_injection(value):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Command injection attempt in field '{key}'"
                        )
                elif isinstance(value, (dict, list)):
                    self.check_json_values(value)

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self.check_json_values(item)
                elif isinstance(item, str):
                    if self.detect_sql_injection(item):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="SQL injection attempt in list"
                        )
                    if self.detect_xss(item):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="XSS attempt in list"
                        )
                    if self.detect_command_injection(item):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Command injection attempt in list"
                        )

    def check_user_agent(self, user_agent: str, endpoint: str) -> None:
        """
        Check User-Agent header for malicious agents.
        
        Raises:
            HTTPException: If malicious user agent is detected
        """
        if not user_agent or len(user_agent) < 10:
            logger.warning("Suspicious User-Agent header")
            return

        user_agent_lower = user_agent.lower()
        for agent in SecurityPatterns.MALICIOUS_USER_AGENTS:
            if agent in user_agent_lower:
                logger.warning(f"Malicious User-Agent detected: {user_agent}")
                try:
                    from app.utils.prometheus import record_security_incident
                    record_security_incident("malicious_user_agent", endpoint)
                except Exception as e:
                    logger.debug(f"Failed to record security metric: {e}")

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Malicious User-Agent detected"
                )

    def check_referer(self, referer: str) -> None:
        """
        Check Referer header for suspicious domains.
        
        Raises:
            HTTPException: If suspicious referer is detected
        """
        if not referer:
            return

        referer_lower = referer.lower()
        for domain in SecurityPatterns.SUSPICIOUS_DOMAINS:
            if domain in referer_lower:
                logger.warning(f"Suspicious referer: {referer}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Suspicious request source"
                )
