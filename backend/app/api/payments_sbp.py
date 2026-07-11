"""
SBP (System for Fast Payments) Integration

QR-code payments processing and webhook handling.
"""

from decimal import Decimal

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.mentor import Mentor
from app.models.payment import Payment as DBPayment
from app.models.payment import PaymentStatus
from app.models.session import Session as DBSession
from app.models.user import User
from app.services.sbp_service import sbp_service


class SBPPaymentCreate(BaseModel):
    """Schema for SBP payment creation."""

    amount: Decimal
    description: str = ""
    session_id: int
    mentor_id: int
    customer_phone: str | None = None


def create_sbp_qr_payment(
    db: Session,
    current_user: User,
    payment_data: SBPPaymentCreate
) -> dict:
    """
    Create SBP QR-code payment.

    Returns QR-code data and payment URL.
    """
    # Verify session exists
    session = db.query(DBSession).filter(DBSession.id == payment_data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Verify mentor exists
    mentor = db.query(Mentor).filter(Mentor.id == payment_data.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    # Create payment record in database
    db_payment = DBPayment(
        student_id=current_user.id,
        mentor_id=payment_data.mentor_id,
        session_id=payment_data.session_id,
        amount=payment_data.amount,
        currency="RUB",
        payment_method="sbp",
        status=PaymentStatus.PENDING,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Create QR-code in SBP
    qr_result = sbp_service.create_qr_code(
        amount=payment_data.amount,
        description=payment_data.description or f"Session payment #{payment_data.session_id}",
        order_id=str(db_payment.id),
        customer_phone=payment_data.customer_phone,
    )

    if "error" in qr_result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"SBP QR-code creation error: {qr_result['error']}"
        )

    # Save qr_id as transaction_id
    db_payment.transaction_id = qr_result.get("qr_id")
    db.commit()

    return {
        "payment_id": db_payment.id,
        "qr_id": qr_result.get("qr_id"),
        "qr_url": qr_result.get("qr_url"),
        "qr_image": qr_result.get("qr_image"),
        "amount": float(payment_data.amount),
        "currency": "RUB",
        "expires_at": qr_result.get("expires_at"),
        "status": "pending",
    }


def check_sbp_payment_status(
    db: Session,
    payment_id: int,
    current_user: User
) -> dict:
    """Check SBP payment status."""
    payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not payment.transaction_id:
        raise HTTPException(status_code=400, detail="QR-code not found for this payment")

    # Check status in SBP
    sbp_status = sbp_service.check_payment_status(payment.transaction_id)

    if "error" not in sbp_status and sbp_status.get("status") == "completed":
            payment.status = PaymentStatus.COMPLETED
            db.commit()

    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "amount": float(payment.amount),
        "sbp_status": sbp_status.get("status"),
        "bank_name": sbp_status.get("bank_name"),
        "transaction_id": sbp_status.get("transaction_id"),
    }


def get_sbp_available_banks() -> dict:
    """Get list of banks supporting SBP."""
    banks_data = sbp_service.get_available_banks()

    if "error" in banks_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Bank list retrieval error: {banks_data['error']}"
        )

    return banks_data


def handle_sbp_webhook_event(
    db: Session,
    event_type: str,
    event_data: dict
) -> bool:
    """
    Handle SBP webhook event.

    Returns True if event was processed successfully.
    """
    if event_type == "payment.completed":
        qr_id = event_data.get("qr_id")

        payment = db.query(DBPayment).filter(
            DBPayment.transaction_id == qr_id
        ).first()

        if payment:
            payment.status = PaymentStatus.COMPLETED
            db.commit()
            return True

    elif event_type == "payment.failed":
        qr_id = event_data.get("qr_id")

        payment = db.query(DBPayment).filter(
            DBPayment.transaction_id == qr_id
        ).first()

        if payment:
            payment.status = PaymentStatus.FAILED
            db.commit()
            return True

    return False
