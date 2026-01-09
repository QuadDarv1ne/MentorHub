"""
Production configuration
Конфигурация для продакшена с усиленной безопасностью
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class ProductionConfig(BaseSettings):
    """Конфигурация для продакшена"""
    
    # Основные настройки
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    ALLOWED_HOSTS: list[str] = ["mentorhub.ru", "www.mentorhub.ru"]
    
    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Безопасность
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "https://mentorhub.ru",
        "https://www.mentorhub.ru"
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: list[str] = ["*"]
    
    # Email (для продакшена используем профессиональный сервис)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.sendgrid.net")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "apikey")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "noreply@mentorhub.ru")
    SMTP_FROM_NAME: str = "MentorHub"
    SMTP_USE_TLS: bool = True
    SMTP_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CONNECTION_TIMEOUT: int = 5
    REDIS_SOCKET_TIMEOUT: int = 5
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    CELERY_TASK_ACKS_LATE: bool = True
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1
    CELERY_TASK_TIME_LIMIT: int = 300
    CELERY_TASK_SOFT_TIME_LIMIT: int = 240
    
    # Лимиты и ограничения
    MAX_REQUESTS_PER_MINUTE: int = 100
    MAX_REQUEST_BODY_SIZE: int = 5 * 1024 * 1024  # 5MB
    MAX_FILE_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Кэширование
    CACHE_DEFAULT_TTL: int = 300  # 5 минут
    CACHE_LONG_TTL: int = 3600    # 1 час
    CACHE_SHORT_TTL: int = 60     # 1 минута
    
    # Мониторинг
    ENABLE_PROMETHEUS: bool = True
    PROMETHEUS_MULTIPROC_DIR: str = "/tmp/prometheus_multiproc_dir"
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "/var/log/mentorhub/backend.log"
    LOG_MAX_BYTES: int = 100 * 1024 * 1024  # 100MB
    LOG_BACKUP_COUNT: int = 10
    
    # Безопасность
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_SECURITY_HEADERS: bool = True
    ENABLE_AUDIT_LOGGING: bool = True
    ENABLE_IP_WHITELIST: bool = False
    ADMIN_WHITELISTED_IPS: list[str] = ["127.0.0.1"]
    
    # WebSocket
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    WEBSOCKET_MAX_CONNECTIONS: int = 1000
    
    # API
    API_RATE_LIMIT: str = "100/minute"
    API_DOCS_ENABLED: bool = False  # Отключаем Swagger в продакшене
    
    # CDN и статика
    CDN_BASE_URL: Optional[str] = None
    STATIC_FILES_CACHE_CONTROL: str = "public, max-age=31536000"  # 1 год
    
    # Резервное копирование
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Ежедневно в 2:00
    BACKUP_RETENTION_DAYS: int = 30
    
    # Health checks
    HEALTH_CHECK_TIMEOUT: int = 5
    HEALTH_CHECK_RETRY_DELAY: int = 1
    
    # Sentry (для мониторинга ошибок)
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "production"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Глобальный экземпляр конфигурации
settings = ProductionConfig()

# Проверка критических настроек
def validate_production_config():
    """Проверяет критические настройки продакшена"""
    errors = []
    
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
        errors.append("SECRET_KEY must be set in production")
    
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL must be set in production")
    
    if settings.DEBUG:
        errors.append("DEBUG should be False in production")
    
    if not settings.ALLOWED_HOSTS:
        errors.append("ALLOWED_HOSTS must be configured")
    
    if not settings.SMTP_PASSWORD:
        errors.append("SMTP credentials must be configured")
    
    return errors