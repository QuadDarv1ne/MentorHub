"""
Configuration module for MentorHub Backend
Handles all environment variables and app settings
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Main application settings"""

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

    # ==================== SERVER ====================
    HOST: str = "0.0.0.0"
    PORT: int = int(os.environ.get("PORT", "8000"))
    RELOAD: bool = True

    # ==================== DATABASE ====================
    DATABASE_URL: str = "postgresql://mentorhub_user:password@localhost/mentorhub"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40

    # ==================== REDIS ====================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # ==================== JWT AUTHENTICATION ====================
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==================== CORS ====================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        # Amvera domains - these will be overridden by environment variables in production
        "https://*.amvera.app",
        "https://*.amvera.io",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

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
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    EMAIL_SENDER: str = "noreply@mentorhub.com"
    EMAIL_SENDER_NAME: str = "MentorHub"

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
    ALLOWED_HOSTS: List[str] = ["*"]
    SECURE_SSL_REDIRECT: bool = True if os.environ.get('ENVIRONMENT') == 'production' else False
    HSTS_SECONDS: int = 31536000

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

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


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
    # Production validations
    assert (
        settings.SECRET_KEY != "your-secret-key-change-in-production"
    ), "❌ ERROR: SECRET_KEY must be changed in production!"
    assert settings.DEBUG is False, "❌ ERROR: DEBUG must be False in production!"
    assert settings.DATABASE_URL.startswith("postgresql://"), "❌ ERROR: Use PostgreSQL in production!"
    assert settings.AGORA_APP_ID, "❌ ERROR: AGORA_APP_ID required in production!"
    assert settings.SESSION_COOKIE_SECURE, "❌ ERROR: SESSION_COOKIE_SECURE must be True in production!"
    assert settings.SECURE_SSL_REDIRECT, "❌ ERROR: SECURE_SSL_REDIRECT must be True in production!"
