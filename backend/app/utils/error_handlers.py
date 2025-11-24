"""
Централизованная обработка ошибок с детальным логированием
"""

import logging
import traceback
from typing import Optional
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Стандартизированный формат ответа об ошибке"""

    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
        path: Optional[str] = None,
        timestamp: Optional[str] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        self.error_code = error_code
        self.path = path
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Преобразование в словарь для JSON ответа"""
        response = {
            "status_code": self.status_code,
            "message": self.message,
            "timestamp": self.timestamp,
        }

        if self.error_code:
            response["error_code"] = self.error_code
        if self.detail:
            response["detail"] = self.detail
        if self.path:
            response["path"] = self.path

        return response


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Обработчик HTTP исключений

    Args:
        request: FastAPI Request
        exc: HTTP исключение

    Returns:
        JSONResponse с деталями ошибки
    """
    error = ErrorResponse(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}",
        path=str(request.url),
    )

    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} | Path: {request.url} | "
        f"IP: {request.client.host if request.client else 'unknown'}"
    )

    return JSONResponse(status_code=exc.status_code, content=error.to_dict())


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Обработчик ошибок валидации данных

    Args:
        request: FastAPI Request
        exc: Ошибка валидации

    Returns:
        JSONResponse с деталями ошибок валидации
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"], "type": error["type"]})

    error_response = ErrorResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation error",
        error_code="VALIDATION_ERROR",
        detail=errors,
        path=str(request.url),
    )

    logger.warning(f"Validation error: {errors} | Path: {request.url}")

    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response.to_dict())


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Обработчик ошибок базы данных

    Args:
        request: FastAPI Request
        exc: SQLAlchemy исключение

    Returns:
        JSONResponse с информацией об ошибке БД
    """
    # Специальная обработка для нарушений целостности
    if isinstance(exc, IntegrityError):
        error = ErrorResponse(
            status_code=status.HTTP_409_CONFLICT,
            message="Database integrity error",
            error_code="INTEGRITY_ERROR",
            detail="A record with this data already exists or violates database constraints",
            path=str(request.url),
        )
        logger.error(f"Database integrity error: {exc} | Path: {request.url}")
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=error.to_dict())

    # Общие ошибки БД
    error = ErrorResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Database error",
        error_code="DATABASE_ERROR",
        detail="An error occurred while processing your request",
        path=str(request.url),
    )

    logger.error(f"Database error: {exc} | Path: {request.url}", exc_info=True)

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error.to_dict())


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Обработчик неожиданных исключений

    Args:
        request: FastAPI Request
        exc: Любое исключение

    Returns:
        JSONResponse с информацией об ошибке
    """
    # Получаем traceback
    tb = traceback.format_exc()

    # Логируем полную информацию об ошибке
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)} | "
        f"Path: {request.url} | "
        f"IP: {request.client.host if request.client else 'unknown'}\n"
        f"Traceback:\n{tb}"
    )

    # В production скрываем детали
    from app.config import is_production

    if is_production():
        error = ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            path=str(request.url),
        )
    else:
        # В development показываем полные детали
        error = ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(exc),
            error_code=type(exc).__name__,
            detail=tb,
            path=str(request.url),
        )

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error.to_dict())


def register_error_handlers(app):
    """
    Регистрация всех обработчиков ошибок в приложении

    Args:
        app: FastAPI приложение
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("✅ Error handlers registered")
