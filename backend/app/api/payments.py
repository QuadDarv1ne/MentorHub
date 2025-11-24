"""
Роуты платежей
API для работы с платежами через Stripe
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal

from app.dependencies import get_db, get_current_user, rate_limit_dependency
from app.models.payment import Payment as DBPayment, PaymentStatus
from app.models.user import User
from app.models.mentor import Mentor
from app.models.session import Session as DBSession
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.services.stripe_service import stripe_service
from app.services.sbp_service import sbp_service
from app.utils.sanitization import sanitize_string, is_safe_string

router = APIRouter()


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список платежей"""
    # Проверка на корректность параметров пагинации
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100

    payments = db.query(DBPayment).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить информацию о платеже по ID"""
    payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    return payment


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Создать платеж"""
    # Санитизация входных данных
    sanitized_currency = sanitize_string(payment.currency) if payment.currency else "USD"
    sanitized_payment_method = sanitize_string(payment.payment_method) if payment.payment_method else None
    sanitized_transaction_id = sanitize_string(payment.transaction_id) if payment.transaction_id else None

    # Проверка на безопасность входных данных
    if sanitized_currency and not is_safe_string(sanitized_currency):
        raise HTTPException(status_code=400, detail="Недопустимые символы в валюте")
    if sanitized_payment_method and not is_safe_string(sanitized_payment_method):
        raise HTTPException(status_code=400, detail="Недопустимые символы в методе оплаты")
    if sanitized_transaction_id and not is_safe_string(sanitized_transaction_id):
        raise HTTPException(status_code=400, detail="Недопустимые символы в ID транзакции")

    # Проверяем, что студент существует
    student = db.query(User).filter(User.id == payment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    # Проверяем, что ментор существует
    mentor = db.query(Mentor).filter(Mentor.id == payment.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")

    # Проверяем, что сессия существует
    session = db.query(DBSession).filter(DBSession.id == payment.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    # Создаем платеж с санитизированными данными
    db_payment = DBPayment(
        student_id=payment.student_id,
        mentor_id=payment.mentor_id,
        session_id=payment.session_id,
        amount=payment.amount,
        currency=sanitized_currency,
        payment_method=sanitized_payment_method,
        transaction_id=sanitized_transaction_id,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment: PaymentUpdate,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить платеж"""
    db_payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")

    # Санитизация входных данных
    sanitized_data = {}
    for key, value in payment.model_dump(exclude_unset=True).items():
        if key in ["payment_method", "transaction_id"] and value is not None:
            sanitized_value = sanitize_string(value)
            if not is_safe_string(sanitized_value):
                field_name = "методе оплаты" if key == "payment_method" else "ID транзакции"
                raise HTTPException(status_code=400, detail=f"Недопустимые символы в {field_name}")
            sanitized_data[key] = sanitized_value
        else:
            sanitized_data[key] = value

    # Обновляем поля
    for key, value in sanitized_data.items():
        setattr(db_payment, key, value)

    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Удалить платеж"""
    db_payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")

    db.delete(db_payment)
    db.commit()
    return None


# ==================== STRIPE INTEGRATION ====================


class PaymentIntentCreate(BaseModel):
    """Схема для создания платежного намерения"""

    amount: Decimal
    currency: str = "usd"
    description: str = ""
    session_id: int
    mentor_id: int


@router.post("/create-intent", response_model=dict)
async def create_payment_intent(
    payment_data: PaymentIntentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Создать платежное намерение Stripe

    Возвращает client_secret для подтверждения платежа на клиенте
    """
    # Проверяем существование сессии
    session = db.query(DBSession).filter(DBSession.id == payment_data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    # Проверяем существование ментора
    mentor = db.query(Mentor).filter(Mentor.id == payment_data.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")

    # Создаем Payment Intent в Stripe
    intent_result = stripe_service.create_payment_intent(
        amount=payment_data.amount,
        currency=payment_data.currency,
        description=payment_data.description or f"Оплата сессии #{payment_data.session_id}",
        metadata={
            "user_id": current_user.id,
            "session_id": payment_data.session_id,
            "mentor_id": payment_data.mentor_id,
        },
    )

    if "error" in intent_result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Ошибка создания платежа: {intent_result['error']}"
        )

    # Создаем запись о платеже в БД
    db_payment = DBPayment(
        student_id=current_user.id,
        mentor_id=payment_data.mentor_id,
        session_id=payment_data.session_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
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
        "amount": float(payment_data.amount),
        "currency": payment_data.currency,
    }


@router.post("/confirm/{payment_id}")
async def confirm_payment(
    payment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Подтвердить успешный платеж"""
    payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")

    if payment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Проверяем статус в Stripe
    if payment.transaction_id:
        stripe_status = stripe_service.retrieve_payment(payment.transaction_id)

        if "error" not in stripe_status:
            if stripe_status.get("status") == "succeeded":
                payment.status = PaymentStatus.COMPLETED
            elif stripe_status.get("status") in ["canceled", "failed"]:
                payment.status = PaymentStatus.FAILED
    else:
        # Mock режим для тестирования
        payment.status = PaymentStatus.COMPLETED

    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "amount": float(payment.amount),
    }


@router.post("/refund/{payment_id}")
async def refund_payment(
    payment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Вернуть средства за платеж"""
    payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")

    # Проверяем права (ментор или админ)
    if payment.mentor_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Возврат возможен только для завершенных платежей")

    # Создаем возврат в Stripe
    if payment.transaction_id:
        refund_result = stripe_service.create_refund(
            payment_intent_id=payment.transaction_id, reason="requested_by_customer"
        )

        if "error" in refund_result:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Ошибка возврата: {refund_result['error']}"
            )

    payment.status = PaymentStatus.REFUNDED
    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "refunded_amount": float(payment.amount),
    }


@router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db), skip: int = 0, limit: int = 20
):
    """Получить историю платежей текущего пользователя"""
    payments = (
        db.query(DBPayment)
        .filter(DBPayment.student_id == current_user.id)
        .order_by(DBPayment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return payments


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook для обработки событий от Stripe

    Stripe отправляет уведомления о статусе платежей
    """
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    # Проверяем подпись webhook
    event = stripe_service.verify_webhook_signature(payload, signature)

    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Обрабатываем событие
    event_type = event.get("type")

    if event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        transaction_id = payment_intent["id"]

        # Находим платеж и обновляем статус
        payment = db.query(DBPayment).filter(DBPayment.transaction_id == transaction_id).first()

        if payment:
            payment.status = PaymentStatus.COMPLETED
            db.commit()

    elif event_type == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        transaction_id = payment_intent["id"]

        payment = db.query(DBPayment).filter(DBPayment.transaction_id == transaction_id).first()

        if payment:
            payment.status = PaymentStatus.FAILED
            db.commit()

    return {"status": "success"}


# ==================== СБП INTEGRATION ====================


class SBPPaymentCreate(BaseModel):
    """Схема для создания платежа через СБП"""

    amount: Decimal
    description: str = ""
    session_id: int
    mentor_id: int
    customer_phone: Optional[str] = None


@router.post("/sbp/create-qr", response_model=dict)
async def create_sbp_qr_code(
    payment_data: SBPPaymentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Создать QR-код для оплаты через СБП

    Возвращает QR-код и URL для оплаты через Систему быстрых платежей
    """
    # Проверяем существование сессии
    session = db.query(DBSession).filter(DBSession.id == payment_data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    # Проверяем существование ментора
    mentor = db.query(Mentor).filter(Mentor.id == payment_data.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")

    # Создаем запись о платеже в БД
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

    # Создаем QR-код в СБП
    qr_result = sbp_service.create_qr_code(
        amount=payment_data.amount,
        description=payment_data.description or f"Оплата сессии #{payment_data.session_id}",
        order_id=str(db_payment.id),
        customer_phone=payment_data.customer_phone,
    )

    if "error" in qr_result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Ошибка создания QR-кода СБП: {qr_result['error']}"
        )

    # Сохраняем qr_id как transaction_id
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


@router.get("/sbp/check-status/{payment_id}")
async def check_sbp_payment_status(
    payment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Проверить статус платежа СБП"""
    payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")

    if payment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    if not payment.transaction_id:
        raise HTTPException(status_code=400, detail="QR-код не найден для этого платежа")

    # Проверяем статус в СБП
    sbp_status = sbp_service.check_payment_status(payment.transaction_id)

    if "error" not in sbp_status:
        if sbp_status.get("status") == "completed":
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


@router.get("/sbp/banks", response_model=dict)
async def get_sbp_banks():
    """
    Получить список банков, поддерживающих СБП

    Возвращает список банков для отображения пользователю
    """
    banks_data = sbp_service.get_available_banks()

    if "error" in banks_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ошибка получения списка банков: {banks_data['error']}",
        )

    return banks_data


@router.post("/sbp/webhook")
async def sbp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook для обработки событий от СБП

    СБП отправляет уведомления о статусе платежей
    """
    payload = await request.body()
    signature = request.headers.get("x-sbp-signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing x-sbp-signature header")

    # Проверяем подпись webhook
    event = sbp_service.verify_webhook_signature(payload, signature)

    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Обрабатываем событие
    event_type = event.get("event_type")

    if event_type == "payment.completed":
        qr_id = event.get("qr_id")

        # Находим платеж и обновляем статус
        payment = db.query(DBPayment).filter(DBPayment.transaction_id == qr_id).first()

        if payment:
            payment.status = PaymentStatus.COMPLETED
            db.commit()

    elif event_type == "payment.failed":
        qr_id = event.get("qr_id")

        payment = db.query(DBPayment).filter(DBPayment.transaction_id == qr_id).first()

        if payment:
            payment.status = PaymentStatus.FAILED
            db.commit()

    return {"status": "success"}
