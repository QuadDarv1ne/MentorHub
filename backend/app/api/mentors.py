"""
Mentors API Router
Объединяет все роуты для работы с менторами
"""

from fastapi import APIRouter
import asyncio
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, rate_limit_dependency, get_current_user
from app.models.mentor import Mentor
from app.models.user import User
from app.schemas.mentor import MentorCreate, MentorUpdate, MentorResponse
from app.utils.sanitization import sanitize_text_field, sanitize_string, is_safe_string
from app.services.cache import cached
from app.utils.cache import invalidate_cache

# Импортируем роутер поиска
from app.api.mentors_search import router as mentors_search_router

router = APIRouter()

# Включаем роутер поиска
router.include_router(mentors_search_router)


@router.get("/", response_model=List[MentorResponse])
@cached(ttl=900, key_prefix="mentors_list")
async def get_mentors(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список менторов"""
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100

    # Используем joinedload для загрузки user данных вместе с ментором (избегаем N+1)
    mentors = db.query(Mentor).options(joinedload(Mentor.user)).offset(skip).limit(limit).all()
    return mentors


@router.get("/{mentor_id}", response_model=MentorResponse)
@cached(ttl=900, key_prefix="mentor_detail")
async def get_mentor(mentor_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)):
    """Получить информацию о менторе по ID"""
    if mentor_id <= 0:
        raise HTTPException(status_code=400, detail="Некорректный ID ментора")

    # Используем joinedload для загрузки user данных вместе с ментором (избегаем N+1)
    mentor = db.query(Mentor).options(joinedload(Mentor.user)).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")
    return mentor


@router.post("/", response_model=MentorResponse, status_code=status.HTTP_201_CREATED)
async def create_mentor(
    mentor: MentorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Создать профиль ментора (только для авторизованных пользователей)"""
    # Пользователь может создать профиль только от своего имени (или админ)
    if mentor.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Вы можете создать профиль только от своего имени.")
    
    # Санитизация входных данных
    sanitized_bio = sanitize_text_field(mentor.bio) if mentor.bio else None
    sanitized_specialization = sanitize_string(mentor.specialization) if mentor.specialization else None

    # Проверка на безопасность входных данных
    if sanitized_bio and not is_safe_string(sanitized_bio):
        raise HTTPException(status_code=400, detail="Недопустимые символы в биографии")
    if sanitized_specialization and not is_safe_string(sanitized_specialization):
        raise HTTPException(status_code=400, detail="Недопустимые символы в специализации")

    # Проверяем, что пользователь существует с использованием joinedload для оптимизации
    user = db.query(User).options(
        joinedload(User.sessions),
        joinedload(User.reviews)
    ).filter(User.id == mentor.user_id).first()
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
    
    try:
        db.commit()
        db.refresh(db_mentor)
        return db_mentor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании профиля ментора: {str(e)}")


@router.put("/{mentor_id}", response_model=MentorResponse)
async def update_mentor(
    mentor_id: int,
    mentor: MentorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить профиль ментора (только владелец или админ)"""
    db_mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not db_mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")
    
    # Проверка ownership: владелец профиля или админ
    if db_mentor.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Вы можете редактировать только свой профиль.")

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

    try:
        db.commit()
        db.refresh(db_mentor)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении профиля ментора: {str(e)}")

    # Инвалидируем кеш обновленного ментора
    asyncio.create_task(invalidate_cache(f"mentor_detail:{db_mentor.id}"))
    asyncio.create_task(invalidate_cache("mentors_list:*"))

    return db_mentor


@router.delete("/{mentor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mentor(
    mentor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Удалить профиль ментора (только владелец или админ)"""
    db_mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not db_mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")
    
    # Проверка ownership: владелец профиля или админ
    if db_mentor.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Вы можете удалить только свой профиль.")

    try:
        db.delete(db_mentor)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении профиля ментора: {str(e)}")

    # Инвалидируем кеш удаленного ментора
    asyncio.create_task(invalidate_cache(f"mentor_detail:{mentor_id}"))
    asyncio.create_task(invalidate_cache("mentors_list:*"))
    return None
