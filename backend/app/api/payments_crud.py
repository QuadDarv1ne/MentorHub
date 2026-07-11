"""
Payments CRUD Operations

Database operations for payments management.
"""

import logging
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.mentor import Mentor
from app.models.payment import Payment as DBPayment
from app.models.payment import PaymentStatus
from app.models.session import Session as DBSession

logger = logging.getLogger(__name__)
from app.models.user import User
from app.schemas.payment import PaymentUpdate
from app.utils.sanitization import is_safe_string, sanitize_string


def get_all_payments(db: Session, skip: int = 0, limit: int = 100) -> list[DBPayment]:
    """Get all payments with pagination."""
    from app.utils.pagination import validate_pagination
    skip, limit = validate_pagination(skip, limit)

    return db.query(DBPayment).options(
        joinedload(DBPayment.student),
        joinedload(DBPayment.mentor),
        joinedload(DBPayment.session)
    ).offset(skip).limit(limit).all()


def get_payment_by_id(db: Session, payment_id: int) -> DBPayment | None:
    """Get payment by ID."""
    return db.query(DBPayment).options(
        joinedload(DBPayment.student),
        joinedload(DBPayment.mentor),
        joinedload(DBPayment.session)
    ).filter(DBPayment.id == payment_id).first()


def get_payments_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[DBPayment]:
    """Get payments by user ID with pagination."""
    return db.query(DBPayment).options(
        joinedload(DBPayment.student),
        joinedload(DBPayment.mentor),
        joinedload(DBPayment.session)
    ).filter(DBPayment.student_id == user_id).order_by(
        DBPayment.created_at.desc()
    ).offset(skip).limit(limit).all()


def create_payment(
    db: Session,
    student_id: int,
    mentor_id: int,
    session_id: int,
    amount: Decimal,
    currency: str = "USD",
    payment_method: str | None = None,
    transaction_id: str | None = None,
    status: PaymentStatus = PaymentStatus.PENDING
) -> DBPayment:
    """Create a new payment."""
    try:
        # Sanitize input data
        sanitized_currency = sanitize_string(currency) if currency else "USD"
        sanitized_payment_method = sanitize_string(payment_method) if payment_method else None
        sanitized_transaction_id = sanitize_string(transaction_id) if transaction_id else None

        # Validate input data
        if sanitized_currency and not is_safe_string(sanitized_currency):
            raise ValueError("Invalid currency characters")
        if sanitized_payment_method and not is_safe_string(sanitized_payment_method):
            raise ValueError("Invalid payment method characters")
        if sanitized_transaction_id and not is_safe_string(sanitized_transaction_id):
            raise ValueError("Invalid transaction ID characters")

        # Verify related entities exist
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            raise ValueError("Student not found")

        mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
        if not mentor:
            raise ValueError("Mentor not found")

        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")

        # Create payment
        db_payment = DBPayment(
            student_id=student_id,
            mentor_id=mentor_id,
            session_id=session_id,
            amount=amount,
            currency=sanitized_currency,
            payment_method=sanitized_payment_method,
            transaction_id=sanitized_transaction_id,
            status=status,
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment
    except Exception:
        logger.exception("Failed to create payment")
        db.rollback()
        raise


def update_payment(
    db: Session,
    payment_id: int,
    payment_data: PaymentUpdate,
    current_user_id: int | None = None
) -> DBPayment | None:
    """Update payment with ownership check."""
    try:
        db_payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
        if not db_payment:
            return None

        # Ownership check: only student or admin can update
        if current_user_id and db_payment.student_id != current_user_id:
            # Check if user is admin (need to query user)
            user = db.query(User).filter(User.id == current_user_id).first()
            if not user or user.role.value != "admin":
                raise ValueError("You don't have permission to update this payment")

        # Sanitize and update fields
        for key, value in payment_data.model_dump(exclude_unset=True).items():
            if key in ["payment_method", "transaction_id"] and value is not None:
                sanitized_value = sanitize_string(value)
                if not is_safe_string(sanitized_value):
                    raise ValueError(f"Invalid characters in {key}")
                setattr(db_payment, key, sanitized_value)
            else:
                setattr(db_payment, key, value)

        db.commit()
        db.refresh(db_payment)
        return db_payment
    except Exception:
        logger.exception("Failed to update payment %s", payment_id)
        db.rollback()
        raise


def delete_payment(
    db: Session,
    payment_id: int,
    current_user_id: int | None = None
) -> bool:
    """Delete payment with ownership check."""
    try:
        db_payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
        if not db_payment:
            return False

        # Ownership check: only student or admin can delete
        if current_user_id and db_payment.student_id != current_user_id:
            user = db.query(User).filter(User.id == current_user_id).first()
            if not user or user.role.value != "admin":
                raise ValueError("You don't have permission to delete this payment")

        db.delete(db_payment)
        db.commit()
        return True
    except Exception:
        logger.exception("Failed to delete payment %s", payment_id)
        db.rollback()
        raise


def update_payment_status(
    db: Session,
    payment_id: int,
    new_status: PaymentStatus
) -> DBPayment | None:
    """Update payment status."""
    try:
        payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
        if not payment:
            return None

        payment.status = new_status
        db.commit()
        db.refresh(payment)
        return payment
    except Exception:
        logger.exception("Failed to update payment status %s", payment_id)
        db.rollback()
        raise


def get_payment_by_transaction_id(
    db: Session,
    transaction_id: str
) -> DBPayment | None:
    """Get payment by transaction ID."""
    return db.query(DBPayment).filter(
        DBPayment.transaction_id == transaction_id
    ).first()
