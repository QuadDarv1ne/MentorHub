"""
Модель платежа
Модель для отслеживания платежей за сессии
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

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

    student_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), index=True, nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), index=True, nullable=False)
    amount = Column(Integer, nullable=False)  # в центах/копейках
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(255), nullable=True, unique=True)

    # Timestamp fields
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
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
