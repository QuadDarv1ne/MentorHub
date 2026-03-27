"""
Anti-Phishing Utilities

URL safety checking and phishing detection.
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse


class AntiPhishingValidator:
    """Validator for phishing protection."""

    # Known phishing keywords
    PHISHING_KEYWORDS: List[str] = [
        "verify",
        "account",
        "suspended",
        "confirm",
        "update",
        "urgent",
        "click here",
        "free money",
        "prize",
        "winner",
        "password reset",
        "security alert",
        "account locked",
    ]

    # Suspicious URL shorteners
    SUSPICIOUS_DOMAINS: List[str] = [
        "bit.ly",
        "tinyurl.com",
        "goo.gl",
        "t.co",
        "ow.ly",
        "buff.ly",
        "adf.ly",
    ]

    # Known phishing TLDs (often used for phishing)
    SUSPICIOUS_TLDS: List[str] = [
        ".tk",
        ".ml",
        ".ga",
        ".cf",
        ".gq",
        ".xyz",
        ".top",
        ".work",
    ]

    @classmethod
    def check_url_safety(cls, url: str) -> Dict:
        """
        Check URL safety for phishing indicators.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with safety analysis
        """
        result = {
            "url": url,
            "is_safe": True,
            "risk_score": 0,
            "warnings": [],
        }

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
        except Exception:
            result["is_safe"] = False
            result["warnings"].append("Invalid URL format")
            return result

        # Check for suspicious domains
        for suspicious_domain in cls.SUSPICIOUS_DOMAINS:
            if suspicious_domain in domain:
                result["risk_score"] += 30
                result["warnings"].append(f"Suspicious domain: {suspicious_domain}")

        # Check for suspicious TLDs
        for tld in cls.SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                result["risk_score"] += 20
                result["warnings"].append(f"Suspicious TLD: {tld}")

        # Check for phishing keywords in path
        for keyword in cls.PHISHING_KEYWORDS:
            if keyword in path:
                result["risk_score"] += 10
                result["warnings"].append(f"Phishing keyword: {keyword}")

        # Check for IP address instead of domain (often used in phishing)
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        if re.match(ip_pattern, domain):
            result["risk_score"] += 25
            result["warnings"].append("IP address instead of domain")

        # Check for excessive subdomains (often used in phishing)
        subdomain_count = domain.count(".")
        if subdomain_count > 3:
            result["risk_score"] += 15
            result["warnings"].append("Excessive subdomains")

        # Check for HTTPS
        if parsed.scheme != "https" and parsed.scheme != "http":
            result["risk_score"] += 10
            result["warnings"].append("Invalid protocol")

        # Determine safety status
        if result["risk_score"] >= 50:
            result["is_safe"] = False
            result["risk_level"] = "high"
        elif result["risk_score"] >= 30:
            result["is_safe"] = True
            result["risk_level"] = "medium"
        else:
            result["is_safe"] = True
            result["risk_level"] = "low"

        return result

    @classmethod
    def is_safe_url(cls, url: str, max_risk_score: int = 40) -> bool:
        """
        Quick check if URL is safe.
        
        Args:
            url: URL to check
            max_risk_score: Maximum acceptable risk score
            
        Returns:
            True if URL is safe, False otherwise
        """
        result = cls.check_url_safety(url)
        return result["is_safe"] and result["risk_score"] <= max_risk_score

    @classmethod
    def check_email_subject(cls, subject: str) -> Dict:
        """
        Check email subject for phishing indicators.
        
        Args:
            subject: Email subject line
            
        Returns:
            Dictionary with analysis
        """
        result = {
            "subject": subject,
            "is_suspicious": False,
            "risk_score": 0,
            "flags": [],
        }

        subject_lower = subject.lower()

        # Check for urgency indicators
        urgency_words = ["urgent", "immediate", "action required", "expire", "last chance"]
        for word in urgency_words:
            if word in subject_lower:
                result["risk_score"] += 15
                result["flags"].append(f"Urgency word: {word}")

        # Check for phishing keywords
        for keyword in cls.PHISHING_KEYWORDS:
            if keyword in subject_lower:
                result["risk_score"] += 10
                result["flags"].append(f"Phishing keyword: {keyword}")

        # Check for excessive punctuation
        if subject.count("!") > 2 or subject.count("?") > 2:
            result["risk_score"] += 10
            result["flags"].append("Excessive punctuation")

        # Check for all caps
        if subject.isupper() and len(subject) > 5:
            result["risk_score"] += 15
            result["flags"].append("All caps")

        # Determine suspicion level
        if result["risk_score"] >= 30:
            result["is_suspicious"] = True

        return result
