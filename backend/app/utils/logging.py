"""
Logging Configuration
Structured logging with file rotation and JSON formatting
"""

import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    json_logs: bool = False,
) -> None:
    """Setup application logging with rotation"""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        JSONFormatter() if json_logs else logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    root_logger.addHandler(console_handler)

    formatter = JSONFormatter() if json_logs else logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    general_file_handler = logging.handlers.RotatingFileHandler(
        log_path / "app.log", maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    general_file_handler.setLevel(logging.INFO)
    general_file_handler.setFormatter(formatter)
    root_logger.addHandler(general_file_handler)

    error_file_handler = logging.handlers.RotatingFileHandler(
        log_path / "error.log", maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    root_logger.addHandler(error_file_handler)

    api_logger = logging.getLogger("api")
    api_logger.setLevel(logging.INFO)
    api_file_handler = logging.handlers.RotatingFileHandler(
        log_path / "api_access.log", maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    api_file_handler.setFormatter(formatter)
    api_logger.addHandler(api_file_handler)
    api_logger.propagate = False

    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.WARNING)
    security_file_handler = logging.handlers.RotatingFileHandler(
        log_path / "security.log", maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    security_file_handler.setFormatter(formatter)
    security_logger.addHandler(security_file_handler)
    security_logger.propagate = False

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    root_logger.info(f"Logging initialized - Level: {log_level}, Directory: {log_dir}")


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with specified name"""
    return logging.getLogger(name)


def log_security_event(event_type: str, user_id: str | None = None, ip_address: str | None = None, details: str | None = None):
    """Log security-related events"""
    logger = logging.getLogger("security")
    extra = {}
    if user_id:
        extra["user_id"] = user_id
    if ip_address:
        extra["ip_address"] = ip_address
    message = f"Security Event: {event_type}"
    if details:
        message += f" - {details}"
    logger.warning(message, extra=extra)


if settings.ENVIRONMENT == "production":
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_dir="logs",
        max_bytes=10 * 1024 * 1024,
        backup_count=10,
        json_logs=True,
    )
else:
    setup_logging(log_level="DEBUG", log_dir="logs", max_bytes=5 * 1024 * 1024, backup_count=3, json_logs=False)
