"""
Модель платежа
Модель для отслеживания платежей за сессии
"""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PaymentStatus(str, enum.Enum):
    """Статусы платежей"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(BaseModel):
    """Модель платежа"""

    __tablename__ = "payments"

    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    mentor_id: Mapped[int] = mapped_column(Integer, ForeignKey("mentors.id"), index=True, nullable=False)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.id"), index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # в центах/копейках
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)

    # Timestamp fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Связи
    student = relationship("User", foreign_keys=[student_id], back_populates="payments")
    mentor = relationship("Mentor", foreign_keys=[mentor_id], back_populates="payments")
    session = relationship("Session", back_populates="payments")

    # Составные индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_payment_status_created', 'status', 'created_at'),
        Index('idx_payment_student_status', 'student_id', 'status'),
        Index('idx_payment_mentor_status', 'mentor_id', 'status'),
    )

    def __repr__(self):
        return f"<Payment(id={self.id}, student_id={self.student_id}, amount={self.amount}, status={self.status})>"
