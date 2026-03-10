"""
Модель платежа
Модель для отслеживания платежей за сессии
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Связи
    # student = relationship("User", foreign_keys=[student_id])
    # mentor = relationship("Mentor", foreign_keys=[mentor_id])
    # session = relationship("Session")

    def __repr__(self):
        return f"<Payment(id={self.id}, student_id={self.student_id}, amount={self.amount}, status={self.status})>"
