"""
Роуты менторов
API для работы с профилями менторов
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, rate_limit_dependency
from app.models.mentor import Mentor
from app.models.user import User
from app.schemas.mentor import MentorCreate, MentorUpdate, MentorResponse

router = APIRouter()


@router.get("/", response_model=List[MentorResponse])
async def get_mentors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить список менторов"""
    mentors = db.query(Mentor).offset(skip).limit(limit).all()
    return mentors


@router.get("/{mentor_id}", response_model=MentorResponse)
async def get_mentor(mentor_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить информацию о менторе по ID"""
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")
    return mentor


@router.post("/", response_model=MentorResponse, status_code=status.HTTP_201_CREATED)
async def create_mentor(mentor: MentorCreate, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Создать профиль ментора"""
    # Проверяем, что пользователь существует
    user = db.query(User).filter(User.id == mentor.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяем, что у пользователя еще нет профиля ментора
    existing_mentor = db.query(Mentor).filter(Mentor.user_id == mentor.user_id).first()
    if existing_mentor:
        raise HTTPException(status_code=400, detail="У пользователя уже есть профиль ментора")
    
    db_mentor = Mentor(**mentor.model_dump())
    db.add(db_mentor)
    db.commit()
    db.refresh(db_mentor)
    return db_mentor


@router.put("/{mentor_id}", response_model=MentorResponse)
async def update_mentor(mentor_id: int, mentor: MentorUpdate, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Обновить профиль ментора"""
    db_mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not db_mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")
    
    for key, value in mentor.model_dump(exclude_unset=True).items():
        setattr(db_mentor, key, value)
    
    db.commit()
    db.refresh(db_mentor)
    return db_mentor


@router.delete("/{mentor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mentor(mentor_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Удалить профиль ментора"""
    db_mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not db_mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")
    
    db.delete(db_mentor)
    db.commit()
    return None

