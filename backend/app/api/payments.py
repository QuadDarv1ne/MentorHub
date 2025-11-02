"""
Роуты платежей
API для работы с платежами
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, rate_limit_dependency
from app.models.payment import Payment as DBPayment
from app.models.user import User
from app.models.mentor import Mentor
from app.models.session import Session as DBSession
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.utils.sanitization import sanitize_string, is_safe_string

router = APIRouter()


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить список платежей"""
    # Проверка на корректность параметров пагинации
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100
    
    payments = db.query(DBPayment).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить информацию о платеже по ID"""
    payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    return payment


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentCreate, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
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
        transaction_id=sanitized_transaction_id
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(payment_id: int, payment: PaymentUpdate, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
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
async def delete_payment(payment_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Удалить платеж"""
    db_payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    db.delete(db_payment)
    db.commit()
    return None

