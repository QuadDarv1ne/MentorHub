"""
Роуты платежей
API для работы с платежами
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.payment import Payment as DBPayment
from app.models.user import User
from app.models.mentor import Mentor
from app.models.session import Session as DBSession
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse

router = APIRouter()


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список платежей"""
    payments = db.query(DBPayment).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """Получить информацию о платеже по ID"""
    payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    return payment


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    """Создать платеж"""
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
    
    db_payment = DBPayment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(payment_id: int, payment: PaymentUpdate, db: Session = Depends(get_db)):
    """Обновить платеж"""
    db_payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    for key, value in payment.model_dump(exclude_unset=True).items():
        setattr(db_payment, key, value)
    
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    """Удалить платеж"""
    db_payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    db.delete(db_payment)
    db.commit()
    return None

