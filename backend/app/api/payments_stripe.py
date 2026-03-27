"""
Stripe Payment Integration

Stripe payment processing and webhook handling.
"""

from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.payment import Payment as DBPayment, PaymentStatus
from app.models.user import User
from app.models.mentor import Mentor
from app.models.session import Session as DBSession
from app.services.stripe_service import stripe_service


def create_stripe_payment_intent(
    db: Session,
    current_user: User,
    amount: Decimal,
    currency: str,
    description: str,
    session_id: int,
    mentor_id: int
) -> dict:
    """
    Create Stripe Payment Intent.
    
    Returns client_secret for payment confirmation on client side.
    """
    # Verify session exists
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Verify mentor exists
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    # Create Payment Intent in Stripe
    intent_result = stripe_service.create_payment_intent(
        amount=amount,
        currency=currency,
        description=description or f"Session payment #{session_id}",
        metadata={
            "user_id": current_user.id,
            "session_id": session_id,
            "mentor_id": mentor_id,
        },
    )

    if "error" in intent_result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Payment creation error: {intent_result['error']}"
        )

    # Create payment record in database
    db_payment = DBPayment(
        student_id=current_user.id,
        mentor_id=mentor_id,
        session_id=session_id,
        amount=amount,
        currency=currency,
        payment_method="stripe",
        transaction_id=intent_result.get("id"),
        status=PaymentStatus.PENDING,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return {
        "client_secret": intent_result.get("client_secret"),
        "payment_id": db_payment.id,
        "amount": float(amount),
        "currency": currency,
    }


def confirm_stripe_payment(
    db: Session,
    payment_id: int,
    current_user: User
) -> dict:
    """Confirm Stripe payment."""
    payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check status in Stripe
    if payment.transaction_id:
        stripe_status = stripe_service.retrieve_payment(payment.transaction_id)

        if "error" not in stripe_status:
            if stripe_status.get("status") == "succeeded":
                payment.status = PaymentStatus.COMPLETED
            elif stripe_status.get("status") in ["canceled", "failed"]:
                payment.status = PaymentStatus.FAILED
    else:
        # Mock mode for testing
        payment.status = PaymentStatus.COMPLETED

    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "amount": float(payment.amount),
    }


def refund_stripe_payment(
    db: Session,
    payment_id: int,
    current_user: User
) -> dict:
    """Refund Stripe payment."""
    payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Check permissions (mentor or admin)
    if payment.mentor_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Refund only available for completed payments"
        )

    # Create refund in Stripe
    if payment.transaction_id:
        refund_result = stripe_service.create_refund(
            payment_intent_id=payment.transaction_id,
            reason="requested_by_customer"
        )

        if "error" in refund_result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Refund error: {refund_result['error']}"
            )

    payment.status = PaymentStatus.REFUNDED
    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "refunded_amount": float(payment.amount),
    }


def handle_stripe_webhook_event(
    db: Session,
    event_type: str,
    event_data: dict
) -> bool:
    """
    Handle Stripe webhook event.
    
    Returns True if event was processed successfully.
    """
    if event_type == "payment_intent.succeeded":
        payment_intent = event_data["data"]["object"]
        transaction_id = payment_intent["id"]

        payment = db.query(DBPayment).filter(
            DBPayment.transaction_id == transaction_id
        ).first()

        if payment:
            payment.status = PaymentStatus.COMPLETED
            db.commit()
            return True

    elif event_type == "payment_intent.payment_failed":
        payment_intent = event_data["data"]["object"]
        transaction_id = payment_intent["id"]

        payment = db.query(DBPayment).filter(
            DBPayment.transaction_id == transaction_id
        ).first()

        if payment:
            payment.status = PaymentStatus.FAILED
            db.commit()
            return True

    return False
