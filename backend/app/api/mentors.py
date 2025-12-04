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
from app.utils.sanitization import sanitize_text_field, sanitize_string, is_safe_string
from app.utils.cache import cached, invalidate_cache, CACHE_TTL

router = APIRouter()


@router.get("/", response_model=List[MentorResponse])
@cached(ttl=CACHE_TTL['mentor'], key_prefix="mentors_list")
async def get_mentors(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список менторов"""
    # Проверка на корректность параметров пагинации
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100

    mentors = db.query(Mentor).offset(skip).limit(limit).all()
    return mentors


@router.get("/{mentor_id}", response_model=MentorResponse)
@cached(ttl=CACHE_TTL['mentor'], key_prefix="mentor_detail")
async def get_mentor(mentor_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить информацию о менторе по ID"""
    # Проверка на корректность ID
    if mentor_id <= 0:
        raise HTTPException(status_code=400, detail="Некорректный ID ментора")

    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")
    return mentor


@router.post("/", response_model=MentorResponse, status_code=status.HTTP_201_CREATED)
async def create_mentor(
    mentor: MentorCreate, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Создать профиль ментора"""
    # Санитизация входных данных
    sanitized_bio = sanitize_text_field(mentor.bio) if mentor.bio else None
    sanitized_specialization = sanitize_string(mentor.specialization) if mentor.specialization else None

    # Проверка на безопасность входных данных
    if sanitized_bio and not is_safe_string(sanitized_bio):
        raise HTTPException(status_code=400, detail="Недопустимые символы в биографии")
    if sanitized_specialization and not is_safe_string(sanitized_specialization):
        raise HTTPException(status_code=400, detail="Недопустимые символы в специализации")

    # Проверяем, что пользователь существует
    user = db.query(User).filter(User.id == mentor.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем, что у пользователя еще нет профиля ментора
    existing_mentor = db.query(Mentor).filter(Mentor.user_id == mentor.user_id).first()
    if existing_mentor:
        raise HTTPException(status_code=400, detail="У пользователя уже есть профиль ментора")

    # Создаем ментора с санитизированными данными
    db_mentor = Mentor(
        user_id=mentor.user_id,
        bio=sanitized_bio,
        specialization=sanitized_specialization,
        experience_years=mentor.experience_years,
        hourly_rate=mentor.hourly_rate,
        is_available=mentor.is_available,
    )
    db.add(db_mentor)
    db.commit()
    db.refresh(db_mentor)
    return db_mentor


@router.put("/{mentor_id}", response_model=MentorResponse)
async def update_mentor(
    mentor_id: int,
    mentor: MentorUpdate,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить профиль ментора"""
    db_mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not db_mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")

    # Санитизация входных данных
    sanitized_data = {}
    for key, value in mentor.model_dump(exclude_unset=True).items():
        if key == "bio" and value is not None:
            sanitized_value = sanitize_text_field(value)
            if not is_safe_string(sanitized_value):
                raise HTTPException(status_code=400, detail="Недопустимые символы в биографии")
            sanitized_data[key] = sanitized_value
        elif key == "specialization" and value is not None:
            sanitized_value = sanitize_string(value)
            if not is_safe_string(sanitized_value):
                raise HTTPException(status_code=400, detail="Недопустимые символы в специализации")
            sanitized_data[key] = sanitized_value
        else:
            sanitized_data[key] = value

    # Обновляем поля
    for key, value in sanitized_data.items():
        setattr(db_mentor, key, value)

    db.commit()
    db.refresh(db_mentor)
    
    # Инвалидируем кеш обновленного ментора
    import asyncio
    asyncio.create_task(invalidate_cache(f"mentor_detail:{db_mentor.id}"))
    asyncio.create_task(invalidate_cache("mentors_list:*"))
    
    return db_mentor


@router.delete("/{mentor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mentor(
    mentor_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Удалить профиль ментора"""
    db_mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not db_mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")

    db.delete(db_mentor)
    db.commit()
    
    # Инвалидируем кеш удаленного ментора
    import asyncio
    asyncio.create_task(invalidate_cache(f"mentor_detail:{mentor_id}"))
    asyncio.create_task(invalidate_cache("mentors_list:*"))
    return None
