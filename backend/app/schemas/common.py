"""
Общие схемы
Общие Pydantic схемы, используемые во всем приложении
"""

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Параметры пагинации"""

    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=20)

    @property
    def skip(self) -> int:
        """Вычисление смещения для пагинации"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Получение лимита для пагинации"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Универсальный ответ с пагинацией"""

    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[T]

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        """Создание ответа с пагинацией"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=items,
        )


class MessageResponse(BaseModel):
    """Простой ответ с сообщением"""

    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""

    detail: str
    error_code: str | None = None
