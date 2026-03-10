"""
Configuration module for MentorHub Backend
Handles all environment variables and app settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator, PrivateAttr
from typing import Optional, List
from functools import lru_cache
import os
import logging


class Settings(BaseSettings):
    """Main application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,  # Allow using both field name and alias
    )

    # ==================== APPLICATION ====================
    APP_NAME: str = "MentorHub API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")

    @field_validator("DEBUG", mode="before")
    @classmethod
    def validate_debug(cls, v):
        """Валидация DEBUG из переменных окружения"""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        # Если в системных переменных DEBUG имеет неправильное значение, игнорируем его
        env_debug = os.environ.get("DEBUG", "")
        if env_debug and env_debug.upper() == "WARN":
            return False
        return bool(v) if v is not None else False

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v):
        """Валидация SECRET_KEY - не允许 использовать значения по умолчанию"""
        if not v or v == "your-secret-key-change-in-production":
            # В production это критическая ошибка, в development - предупреждение
            if os.environ.get("ENVIRONMENT") == "production":
                raise ValueError("SECRET_KEY must be set in production! Use a strong random key.")
            # Для development генерируем временный ключ
            import secrets
            logger_warning = logging.getLogger("config")
            logger_warning.warning("⚠️ SECRET_KEY not set, using temporary key. Set SECRET_KEY env var!")
            return secrets.token_urlsafe(32)
        # Проверка на слабые ключи
        if len(v) < 32:
            if os.environ.get("ENVIRONMENT") == "production":
                raise ValueError("SECRET_KEY must be at least 32 characters in production!")
        return v

    # ==================== SERVER ====================
    HOST: str = "0.0.0.0"
    PORT: int = int(os.environ.get("PORT", "8000"))
    RELOAD: bool = True

    # ==================== DATABASE ====================
    # Auto-detect cloud/Docker environment
    _is_docker = os.path.exists("/.dockerenv") or "KUBERNETES_SERVICE_HOST" in os.environ
    _is_render = "RENDER" in os.environ or "RENDER_EXTERNAL_HOST" in os.environ
    _is_railway = "RAILWAY" in os.environ or "RAILWAY_SERVICE_NAME" in os.environ
    _is_fly = "FLY" in os.environ or "FLY_APP_NAME" in os.environ
    _is_cloud = _is_docker or _is_render or _is_railway or _is_fly

    # Cloud providers set DATABASE_URL directly - always use it if available
    _default_db_host = "postgres" if _is_cloud and not _is_render else "localhost"
    _default_redis_host = "redis" if _is_cloud else "localhost"

    # Priority: DATABASE_URL env var > cloud default > local default
    DATABASE_URL: str = os.environ.get("DATABASE_URL") or f"postgresql://mentorhub_user:password@{_default_db_host}/mentorhub"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40

    # ==================== REDIS ====================
    REDIS_URL: str = os.environ.get("REDIS_URL", f"redis://{_default_redis_host}:6379/0")
    REDIS_HOST: str = os.environ.get("REDIS_HOST", _default_redis_host)
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", "6379"))
    REDIS_DB: int = 0

    # ==================== JWT AUTHENTICATION ====================
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==================== CORS ====================
    # Raw CORS string from environment (comma-separated)
    # Using str type to avoid JSON parsing - we parse it manually
    CORS_ORIGINS_RAW: str = ""
    
    # Base CORS origins - always included
    _base_cors_origins: List[str] = []
    
    # Development origins - only for local development
    _dev_cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # CORS_ORIGINS is constructed from:
    # 1. Environment variable CORS_ORIGINS (comma-separated) - highest priority
    # 2. Default origins based on environment
    @model_validator(mode="after")
    def setup_cors_origins(self):
        """Setup CORS origins based on environment"""
        # Get CORS_ORIGINS directly from environment (bypassing pydantic)
        env_cors = os.environ.get("CORS_ORIGINS", "").strip()
        
        if env_cors:
            # Use explicitly set CORS_ORIGINS from environment (comma-separated)
            cors_list = [origin.strip() for origin in env_cors.split(",") if origin.strip()]
        elif os.environ.get("ENVIRONMENT") == "production":
            # Production: only use base origins (should be set via FRONTEND_URL, APP_URL, etc.)
            cors_list = self._base_cors_origins.copy()
        else:
            # Development: include localhost origins
            cors_list = self._base_cors_origins + self._dev_cors_origins
        
        # Validate CORS origins in production
        if os.environ.get("ENVIRONMENT") == "production":
            if "*" in cors_list or any(origin == "*" for origin in cors_list):
                raise ValueError("CORS_ORIGINS cannot contain '*' in production! Specify exact origins.")
            # Check for HTTPS origins in production
            for origin in cors_list:
                if not origin.startswith("https://") and "localhost" not in origin:
                    logging.getLogger("config").warning(
                        f"⚠️ CORS origin '{origin}' does not use HTTPS in production!"
                    )
        
        self._cors_origins = cors_list
        return self

    # Private attribute - not a pydantic field
    _cors_origins: List[str] = PrivateAttr(default_factory=list)
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins"""
        return self._cors_origins
    
    @CORS_ORIGINS.setter
    def CORS_ORIGINS(self, value: List[str]):
        """Set CORS origins"""
        self._cors_origins = value
    
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["Authorization", "Content-Type", "X-CSRF-Token", "X-Request-ID"]

    # ==================== AGORA VIDEO ====================
    AGORA_APP_ID: str = ""
    AGORA_APP_CERTIFICATE: str = ""

    # ==================== STRIPE PAYMENTS ====================
    STRIPE_API_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # ==================== СБП (Система быстрых платежей) ====================
    SBP_MERCHANT_ID: str = ""
    SBP_API_KEY: str = ""
    SBP_SECRET_KEY: str = ""
    SBP_API_URL: str = "https://api.sbp.ru/v1"

    # ==================== YANDEX KASSA ====================
    YANDEX_SHOP_ID: str = ""
    YANDEX_API_KEY: str = ""

    # ==================== AWS S3 ====================
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "mentorhub-bucket"
    AWS_S3_REGION: str = "us-east-1"

    # ==================== EMAIL CONFIGURATION ====================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@mentorhub.com"
    SMTP_FROM_NAME: str = "MentorHub"
    FRONTEND_URL: str = "http://localhost:3001"
    
    # ==================== FIREBASE CLOUD MESSAGING ====================
    FCM_SERVER_KEY: str = ""
    FCM_PROJECT_ID: str = ""
    FCM_SENDER_ID: str = ""

    # ==================== SENTRY ====================
    SENTRY_DSN: Optional[str] = None

    # ==================== CELERY ====================
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"

    # ==================== LOGGING ====================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None

    # ==================== RATE LIMITING ====================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour

    # ==================== SESSION ====================
    SESSION_EXPIRE_DAYS: int = 7
    SESSION_COOKIE_SECURE: bool = True if os.environ.get('ENVIRONMENT') == 'production' else False
    SESSION_COOKIE_HTTPONLY: bool = True

    # ==================== SECURITY ====================
    ALLOWED_HOSTS: List[str] = []
    SECURE_SSL_REDIRECT: bool = True if os.environ.get('ENVIRONMENT') == 'production' else False
    HSTS_SECONDS: int = 31536000

    @model_validator(mode='after')
    def validate_allowed_hosts(self):
        """Валидация ALLOWED_HOSTS - запрет wildcard в production"""
        if self.ENVIRONMENT == "production":
            if "*" in self.ALLOWED_HOSTS or any(host == "*" for host in self.ALLOWED_HOSTS):
                raise ValueError("ALLOWED_HOSTS cannot contain '*' in production!")
            # Если пустой список - добавляем .onrender.com для Render
            if not self.ALLOWED_HOSTS:
                render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
                if render_host:
                    self.ALLOWED_HOSTS = [render_host, ".onrender.com"]
                else:
                    self.ALLOWED_HOSTS = [".onrender.com"]  # Fallback для Render
        return self

    # ==================== FEATURE FLAGS ====================
    FEATURE_VIDEO_SESSIONS: bool = True
    FEATURE_COURSES: bool = True
    FEATURE_LIVE_CHAT: bool = True
    FEATURE_PAYMENTS: bool = True
    FEATURE_EMAIL_NOTIFICATIONS: bool = True

    # ==================== PAGINATION ====================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ==================== FILE UPLOAD ====================
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]

    # ==================== PUSH NOTIFICATIONS ====================
    PUSH_NOTIFICATIONS_ENABLED: bool = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Using @lru_cache to avoid creating new instance on every request
    """
    return Settings()


# Export for easy import
settings = get_settings()


# ==================== ENVIRONMENT CHECKS ====================
def is_production() -> bool:
    """Check if running in production"""
    return settings.ENVIRONMENT == "production"


def is_development() -> bool:
    """Check if running in development"""
    return settings.ENVIRONMENT == "development"


def is_testing() -> bool:
    """Check if running in testing"""
    return settings.ENVIRONMENT == "testing"


# ==================== DATABASE HELPERS ====================
def get_database_url() -> str:
    """Get database URL with proper formatting"""
    return settings.DATABASE_URL


def get_redis_url() -> str:
    """Get Redis URL with proper formatting"""
    return settings.REDIS_URL


# ==================== VALIDATION ====================
if is_production():
    # Production validations (warnings, not errors)
    if settings.SECRET_KEY == "your-secret-key-change-in-production" or not settings.SECRET_KEY:
        logging.warning("⚠️ WARNING: SECRET_KEY not set in production!")
    if settings.DEBUG is True:
        logging.warning("⚠️ WARNING: DEBUG is True in production!")
    if not settings.DATABASE_URL.startswith("postgresql://"):
        logging.warning("⚠️ WARNING: DATABASE_URL not configured properly!")
    # Check if DATABASE_URL is using default fallback (indicates missing env var)
    if "localhost" in settings.DATABASE_URL or "127.0.0.1" in settings.DATABASE_URL:
        logging.warning("⚠️ WARNING: DATABASE_URL using localhost fallback! Set DATABASE_URL env var.")
    if not settings.AGORA_APP_ID:
        logging.warning("⚠️ WARNING: AGORA_APP_ID not set in production!")
    if not settings.SESSION_COOKIE_SECURE:
        logging.warning("⚠️ WARNING: SESSION_COOKIE_SECURE is False in production!")
    if not settings.SECURE_SSL_REDIRECT:
        logging.warning("⚠️ WARNING: SECURE_SSL_REDIRECT is False in production!")
    # CORS validation
    if "*" in settings.CORS_ORIGINS:
        logging.warning("⚠️ WARNING: CORS_ORIGINS contains '*' in production!")
    # Rate limiting validation
    if not settings.RATE_LIMIT_ENABLED:
        logging.warning("⚠️ WARNING: Rate limiting is disabled in production!")
