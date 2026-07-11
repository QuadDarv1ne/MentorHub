"""
Схемы платежей
Pydantic схемы для операций с платежами
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PaymentStatus(str, Enum):
    """Статусы платежей"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentBase(BaseModel):
    """Базовая схема платежа"""

    amount: int = Field(..., gt=0)  # в центах/копейках
    currency: str = Field("USD", min_length=3, max_length=3)
    payment_method: str | None = Field(None, max_length=50)
    transaction_id: str | None = Field(None, max_length=255)


class PaymentCreate(PaymentBase):
    """Схема для создания платежа"""

    student_id: int
    mentor_id: int
    session_id: int


class PaymentUpdate(BaseModel):
    """Схема для обновления платежа"""

    status: PaymentStatus | None = None
    transaction_id: str | None = Field(None, max_length=255)


class PaymentResponse(PaymentBase):
    """Схема ответа с данными платежа"""

    id: int
    student_id: int
    mentor_id: int
    session_id: int
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
