"""
Payments API Router

Payment processing endpoints (Stripe, SBP).
"""

from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, rate_limit_dependency, webhook_rate_limit_dependency
from app.models.user import User
from app.schemas.payment import PaymentResponse, PaymentCreate, PaymentUpdate
from app.api.payments_crud import (
    get_all_payments,
    get_payment_by_id,
    get_payments_by_user,
    create_payment as create_payment_crud,
    update_payment as update_payment_crud,
    delete_payment as delete_payment_crud,
)
from app.api.payments_stripe import (
    create_stripe_payment_intent,
    confirm_stripe_payment,
    refund_stripe_payment,
    handle_stripe_webhook_event,
)
from app.api.payments_sbp import (
    create_sbp_qr_payment,
    check_sbp_payment_status,
    get_sbp_available_banks,
    handle_sbp_webhook_event,
    SBPPaymentCreate,
)

router = APIRouter()


# ==================== CRUD ENDPOINTS ====================

@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Get all payments (admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return get_all_payments(db, skip, limit)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Get payment by ID."""
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Пользователь может видеть только свои платежи
    if current_user.role.value != "admin" and payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    return payment


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Create a new payment."""
    # Пользователь может создавать платежи только от своего имени (или админ)
    if payment.student_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    try:
        return create_payment_crud(
            db=db,
            student_id=current_user.id,
            mentor_id=payment.mentor_id,
            session_id=payment.session_id,
            amount=payment.amount,
            currency=payment.currency or "USD",
            payment_method=payment.payment_method,
            transaction_id=payment.transaction_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment: PaymentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Update payment."""
    existing_payment = get_payment_by_id(db, payment_id)
    if not existing_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Только админ может обновлять платежи
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    try:
        updated = update_payment_crud(db, payment_id, payment)
        if not updated:
            raise HTTPException(status_code=404, detail="Payment not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Delete payment (admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    if not delete_payment_crud(db, payment_id):
        raise HTTPException(status_code=404, detail="Payment not found")


@router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """Get current user's payment history."""
    return get_payments_by_user(db, current_user.id, skip, limit)


# ==================== STRIPE ENDPOINTS ====================

class PaymentIntentCreate(BaseModel):
    """Schema for Stripe payment intent creation."""

    amount: Decimal
    currency: str = "usd"
    description: str = ""
    session_id: int
    mentor_id: int


@router.post("/create-intent", response_model=dict)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe payment intent."""
    return create_stripe_payment_intent(
        db=db,
        current_user=current_user,
        amount=payment_data.amount,
        currency=payment_data.currency,
        description=payment_data.description,
        session_id=payment_data.session_id,
        mentor_id=payment_data.mentor_id,
    )


@router.post("/confirm/{payment_id}")
async def confirm_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm Stripe payment."""
    return confirm_stripe_payment(db, payment_id, current_user)


@router.post("/refund/{payment_id}")
async def refund_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refund Stripe payment."""
    return refund_stripe_payment(db, payment_id, current_user)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(webhook_rate_limit_dependency)
):
    """Handle Stripe webhook events."""
    from app.services.stripe_service import stripe_service

    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    event = stripe_service.verify_webhook_signature(payload, signature)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if handle_stripe_webhook_event(db, event.get("type"), event):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Event processing failed")


# ==================== SBP ENDPOINTS ====================

@router.post("/sbp/create-qr", response_model=dict)
async def create_sbp_qr_code(
    payment_data: SBPPaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create SBP QR-code for payment."""
    return create_sbp_qr_payment(db, current_user, payment_data)


@router.get("/sbp/check-status/{payment_id}")
async def check_sbp_payment_status(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check SBP payment status."""
    return check_sbp_payment_status(db, payment_id, current_user)


@router.get("/sbp/banks", response_model=dict)
async def get_sbp_banks():
    """Get list of banks supporting SBP."""
    return get_sbp_available_banks()


@router.post("/sbp/webhook")
async def sbp_webhook(
    request: Request,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(webhook_rate_limit_dependency)
):
    """Handle SBP webhook events."""
    from app.services.sbp_service import sbp_service

    payload = await request.body()
    signature = request.headers.get("x-sbp-signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing x-sbp-signature header")

    event = sbp_service.verify_webhook_signature(payload, signature)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if handle_sbp_webhook_event(db, event.get("event_type"), event):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Event processing failed")
