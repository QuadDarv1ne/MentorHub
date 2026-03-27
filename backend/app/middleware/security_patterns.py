"""
Security Attack Detection Patterns

Centralized storage of security patterns for detecting various attacks.
"""

import re
from typing import List, Pattern


class SecurityPatterns:
    """Security patterns for attack detection."""

    # SQL Injection patterns
    SQL_INJECTION_PATTERNS: List[str] = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))union",
        r"exec(\s|\+)+(s|x)p\w+",
        r"UNION.*SELECT",
        r"INSERT.*INTO",
        r"DELETE.*FROM",
        r"DROP.*TABLE",
        r"UPDATE.*SET",
        r"EXEC.*SP_",
        r"CREATE.*TABLE",
        r"ALTER.*TABLE",
        r"GRANT.*TO",
        r"REVOKE.*FROM",
    ]

    # XSS patterns
    XSS_PATTERNS: List[str] = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<embed",
        r"<object",
        r"eval\(",
        r"expression\(",
        r"vbscript:",
        r"alert\(",
        r"document\.cookie",
        r"document\.write",
        r"window\.location",
        r"innerHTML",
        r"fromCharCode",
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS: List[str] = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"\.\.\\",
    ]

    # Command injection patterns
    COMMAND_INJECTION_PATTERNS: List[str] = [
        r";\s*(ls|cat|wget|curl|chmod|rm|mv|cp)",
        r"\|\s*(ls|cat|wget|curl)",
        r"`.*`",
        r"\$\(.*\)",
        r"\&\&\s*(ls|cat|wget|curl)",
        r"\|\|\s*(ls|cat|wget|curl)",
        r">\s*/dev/(null|zero)",
        r"\$\{.*\}",
    ]

    # Malicious User-Agents
    MALICIOUS_USER_AGENTS: List[str] = [
        "sqlmap",
        "nikto",
        "nmap",
        "masscan",
        "acunetix",
        "dirbuster",
        "burp",
    ]

    # Suspicious domains for referer checking
    SUSPICIOUS_DOMAINS: List[str] = [
        "bit.ly",
        "tinyurl.com",
        "goo.gl",
        "t.co",
        "ow.ly",
    ]

    @classmethod
    def get_compiled_patterns(cls, pattern_list: List[str]) -> List[Pattern]:
        """Compile regex patterns for better performance."""
        return [re.compile(p, re.IGNORECASE) for p in pattern_list]
