"""
Mentor Search and Filtering API
Расширенный поиск и фильтрация менторов
"""


from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, rate_limit_dependency
from app.models.mentor import Mentor
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.mentor import MentorResponse
from app.services.cache import cached

router = APIRouter()


@router.get("/search", response_model=PaginatedResponse[MentorResponse])
@cached(ttl=600, key_prefix="mentors_search")
async def search_mentors(
    # Search parameters
    query: str | None = Query(None, description="Поиск по имени или специализации"),
    specialization: str | None = Query(None, description="Фильтр по специализации"),

    # Price filters
    min_rate: float | None = Query(None, ge=0, description="Минимальная ставка в час"),
    max_rate: float | None = Query(None, ge=0, description="Максимальная ставка в час"),

    # Experience filters
    min_experience: int | None = Query(None, ge=0, description="Минимальный опыт (лет)"),
    max_experience: int | None = Query(None, ge=0, description="Максимальный опыт (лет)"),

    # Availability
    is_available: bool | None = Query(None, description="Только доступные менторы"),

    # Sorting
    sort_by: str = Query("rating", description="Сортировка: rating, price, experience, name"),
    sort_order: str = Query("desc", description="Порядок: asc, desc"),

    # Pagination
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),

    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """
    Расширенный поиск менторов с фильтрацией и сортировкой

    Параметры:
    - query: Поиск по имени пользователя или специализации
    - specialization: Точная фильтрация по специализации
    - min_rate/max_rate: Диапазон цен
    - min_experience/max_experience: Диапазон опыта
    - is_available: Только доступные менторы
    - sort_by: Поле для сортировки (rating, price, experience, name)
    - sort_order: Порядок сортировки (asc, desc)
    """

    # Base query with joinedload to avoid N+1
    query_obj = db.query(Mentor).options(
        joinedload(Mentor.user),
    )

    # Build filters
    filters = []

    # Text search (name or specialization)
    if query:
        search_term = f"%{query.lower()}%"
        filters.append(
            or_(
                func.lower(User.full_name).like(search_term),
                func.lower(Mentor.specialization).like(search_term),
                func.lower(Mentor.bio).like(search_term)
            )
        )
        query_obj = query_obj.join(User)

    # Specialization filter
    if specialization:
        filters.append(func.lower(Mentor.specialization) == specialization.lower())

    # Price range
    if min_rate is not None:
        filters.append(Mentor.hourly_rate >= min_rate)
    if max_rate is not None:
        filters.append(Mentor.hourly_rate <= max_rate)

    # Experience range
    if min_experience is not None:
        filters.append(Mentor.experience_years >= min_experience)
    if max_experience is not None:
        filters.append(Mentor.experience_years <= max_experience)

    # Availability
    if is_available is not None:
        filters.append(Mentor.is_available == is_available)

    # Apply filters
    if filters:
        query_obj = query_obj.filter(and_(*filters))

    # Sorting
    sort_field_map = {
        "rating": Mentor.rating,
        "price": Mentor.hourly_rate,
        "experience": Mentor.experience_years,
        "name": User.full_name,
    }

    sort_field = sort_field_map.get(sort_by, Mentor.rating)

    if sort_by == "name":
        query_obj = query_obj.join(User) if not query else query_obj

    if sort_order.lower() == "asc":
        query_obj = query_obj.order_by(sort_field.asc())  # type: ignore[attr-defined]
    else:
        query_obj = query_obj.order_by(sort_field.desc())  # type: ignore[attr-defined]

    # Count total
    total = query_obj.count()

    # Pagination
    offset = (page - 1) * page_size
    mentors = query_obj.offset(offset).limit(page_size).all()

    return PaginatedResponse.create(mentors, total, page, page_size)


@router.get("/specializations", response_model=list[str])
@cached(ttl=3600, key_prefix="mentor_specializations")
async def get_specializations(
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """
    Получить список всех уникальных специализаций менторов
    """
    specializations = (
        db.query(Mentor.specialization)
        .filter(Mentor.specialization.isnot(None))
        .distinct()
        .all()
    )

    return [spec[0] for spec in specializations if spec[0]]


@router.get("/top-rated", response_model=list[MentorResponse])
@cached(ttl=1800, key_prefix="mentors_top_rated")
async def get_top_rated_mentors(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """
    Получить топ менторов по рейтингу
    """
    return (
        db.query(Mentor)
        .options(joinedload(Mentor.user))
        .filter(Mentor.rating > 0)
        .order_by(Mentor.rating.desc())
        .limit(limit)
        .all()
    )
