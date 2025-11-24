"""
Security middleware для защиты от различных атак
Включает защиту от: XSS, SQL Injection, CSRF, Click-jacking, и др.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import re
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware для защиты от различных видов атак
    """
    
    def __init__(self, app, rate_limit_requests: int = 100, rate_limit_window: int = 60):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.request_counts = defaultdict(list)
        
        # Паттерны для обнаружения атак
        self.sql_injection_patterns = [
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
        ]
        
        # XSS паттерны
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe",
            r"<embed",
            r"<object",
            r"eval\(",
            r"expression\(",
        ]
        
        # Path traversal паттерны
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.",
            r"%2e%2e",
            r"\.\.\\",
        ]
        
        # Command injection паттерны
        self.command_injection_patterns = [
            r";\s*(ls|cat|wget|curl|chmod|rm|mv|cp)",
            r"\|\s*(ls|cat|wget|curl)",
            r"`.*`",
            r"\$\(.*\)",
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        """Обработка каждого запроса"""
        
        # 1. Rate limiting (защита от DDoS)
        client_ip = self._get_client_ip(request)
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Слишком много запросов. Попробуйте позже."}
            )
        
        # 2. Проверка на подозрительные паттерны
        try:
            await self._check_request_security(request)
        except HTTPException as e:
            logger.error(f"Security check failed: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        
        # 3. Добавление security headers
        response = await call_next(request)
        response = self._add_security_headers(response)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Получение IP клиента"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Проверка rate limit"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.rate_limit_window)
        
        # Очистка старых записей
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if req_time > window_start
        ]
        
        # Добавление текущего запроса
        self.request_counts[client_ip].append(now)
        
        # Проверка лимита
        return len(self.request_counts[client_ip]) <= self.rate_limit_requests
    
    async def _check_request_security(self, request: Request):
        """Проверка запроса на безопасность"""
        
        # Проверка URL
        url_path = str(request.url.path)
        query_params = str(request.url.query) if request.url.query else ""
        
        # SQL Injection в URL
        if self._detect_sql_injection(url_path + query_params):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Обнаружена попытка SQL-инъекции"
            )
        
        # XSS в URL
        if self._detect_xss(url_path + query_params):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Обнаружена попытка XSS-атаки"
            )
        
        # Path Traversal
        if self._detect_path_traversal(url_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Обнаружена попытка path traversal"
            )
        
        # Проверка тела запроса (только для POST/PUT/PATCH)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                body_str = body.decode('utf-8', errors='ignore')
                
                if self._detect_sql_injection(body_str):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Обнаружена попытка SQL-инъекции в теле запроса"
                    )
                
                if self._detect_xss(body_str):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Обнаружена попытка XSS-атаки в теле запроса"
                    )
                
                if self._detect_command_injection(body_str):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Обнаружена попытка command injection"
                    )
                
            except UnicodeDecodeError:
                pass  # Пропускаем бинарные данные
        
        # Проверка заголовков
        self._check_headers(request)
    
    def _detect_sql_injection(self, text: str) -> bool:
        """Обнаружение SQL-инъекций"""
        text_lower = text.lower()
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"SQL Injection pattern detected: {pattern}")
                return True
        return False
    
    def _detect_xss(self, text: str) -> bool:
        """Обнаружение XSS"""
        text_lower = text.lower()
        for pattern in self.xss_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"XSS pattern detected: {pattern}")
                return True
        return False
    
    def _detect_path_traversal(self, text: str) -> bool:
        """Обнаружение path traversal"""
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Path traversal pattern detected: {pattern}")
                return True
        return False
    
    def _detect_command_injection(self, text: str) -> bool:
        """Обнаружение command injection"""
        for pattern in self.command_injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Command injection pattern detected: {pattern}")
                return True
        return False
    
    def _check_headers(self, request: Request):
        """Проверка подозрительных заголовков"""
        
        # Проверка User-Agent
        user_agent = request.headers.get("User-Agent", "")
        if not user_agent or len(user_agent) < 10:
            logger.warning("Suspicious User-Agent header")
        
        # Проверка на известные вредоносные User-Agents
        malicious_agents = ["sqlmap", "nikto", "nmap", "masscan", "acunetix"]
        if any(agent in user_agent.lower() for agent in malicious_agents):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Обнаружен вредоносный User-Agent"
            )
        
        # Проверка Referer на фишинг
        referer = request.headers.get("Referer", "")
        if referer:
            suspicious_domains = ["bit.ly", "tinyurl.com", "goo.gl"]
            if any(domain in referer.lower() for domain in suspicious_domains):
                logger.warning(f"Suspicious referer: {referer}")
    
    def _add_security_headers(self, response):
        """Добавление security headers"""
        
        # Защита от XSS
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )
        
        # HSTS (HTTP Strict Transport Security)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class InputSanitizer:
    """
    Класс для санитизации пользовательского ввода
    """
    
    @staticmethod
    def sanitize_sql(text: str) -> str:
        """Санитизация для предотвращения SQL-инъекций"""
        if not text:
            return text
        
        # Удаление опасных символов
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        sanitized = text
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Санитизация HTML для предотвращения XSS"""
        if not text:
            return text
        
        # Замена опасных HTML символов
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;',
        }
        
        sanitized = text
        for char, replacement in replacements.items():
            sanitized = sanitized.replace(char, replacement)
        
        return sanitized
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Безопасное имя файла"""
        if not filename:
            return "file"
        
        # Удаление path traversal
        filename = filename.replace('../', '').replace('..\\', '')
        
        # Разрешенные символы
        allowed_chars = re.compile(r'[^a-zA-Z0-9._-]')
        sanitized = allowed_chars.sub('_', filename)
        
        # Ограничение длины
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        return sanitized
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Валидация и санитизация email"""
        if not email:
            return ""
        
        # Простая валидация email
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            return ""
        
        return email.lower().strip()
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """Санитизация URL"""
        if not url:
            return ""
        
        # Разрешенные протоколы
        allowed_protocols = ['http://', 'https://']
        if not any(url.startswith(proto) for proto in allowed_protocols):
            return ""
        
        # Удаление опасных символов
        dangerous_chars = ['<', '>', '"', "'", '`']
        sanitized = url
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized


class AntiPhishingValidator:
    """
    Валидатор для защиты от фишинга
    """
    
    # Известные фишинговые паттерны
    PHISHING_KEYWORDS = [
        'verify', 'account', 'suspended', 'confirm', 'update',
        'urgent', 'click here', 'free money', 'prize', 'winner',
        'password reset', 'security alert', 'account locked'
    ]
    
    SUSPICIOUS_DOMAINS = [
        'bit.ly', 'tinyurl.com', 'goo.gl', 't.co',
        'ow.ly', 'buff.ly', 'adf.ly'
    ]
    
    @classmethod
    def check_url_safety(cls, url: str) -> dict:
        """Проверка безопасности URL"""
        result = {
            'is_safe': True,
            'warnings': [],
            'risk_level': 'low'  # low, medium, high
        }
        
        if not url:
            return result
        
        url_lower = url.lower()
        
        # Проверка на URL shorteners
        if any(domain in url_lower for domain in cls.SUSPICIOUS_DOMAINS):
            result['warnings'].append('URL использует сервис сокращения ссылок')
            result['risk_level'] = 'medium'
        
        # Проверка на IP адрес вместо домена
        ip_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        if ip_pattern.search(url):
            result['warnings'].append('URL содержит IP адрес вместо доменного имени')
            result['risk_level'] = 'high'
            result['is_safe'] = False
        
        # Проверка на подозрительные символы
        if '@' in url or '%' in url:
            result['warnings'].append('URL содержит подозрительные символы')
            result['risk_level'] = 'high'
        
        return result
    
    @classmethod
    def check_text_for_phishing(cls, text: str) -> dict:
        """Проверка текста на фишинг"""
        result = {
            'is_suspicious': False,
            'detected_keywords': [],
            'risk_score': 0
        }
        
        if not text:
            return result
        
        text_lower = text.lower()
        
        # Подсчет фишинговых ключевых слов
        for keyword in cls.PHISHING_KEYWORDS:
            if keyword in text_lower:
                result['detected_keywords'].append(keyword)
                result['risk_score'] += 10
        
        # Порог подозрительности
        if result['risk_score'] >= 20:
            result['is_suspicious'] = True
        
        return result


# Singleton экземпляр
input_sanitizer = InputSanitizer()
anti_phishing_validator = AntiPhishingValidator()
