"""
Роуты сессий
API для работы с сессиями менторства
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.dependencies import get_current_user, get_current_user_mentor_id, get_db, rate_limit_dependency
from app.models.mentor import Mentor
from app.models.session import Session as DBSession
from app.models.user import User
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.utils.sanitization import sanitize_and_validate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[SessionResponse])
async def get_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить список сессий (только для администраторов)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права администратора.")

    from app.utils.pagination import validate_pagination
    skip, limit = validate_pagination(skip, limit)

    return db.query(DBSession).options(
        joinedload(DBSession.mentor),
        selectinload(DBSession.student)
    ).offset(skip).limit(limit).all()


@router.get("/my", response_model=list[SessionResponse])
async def get_my_sessions(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mentor_id: int | None = Depends(get_current_user_mentor_id),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить список сессий текущего пользователя (как студента или ментора)"""

    # Build query for sessions where user is either student or mentor
    query = db.query(DBSession).filter(
        (DBSession.student_id == current_user.id) |
        (DBSession.mentor_id == mentor_id if mentor_id else False)
    ).options(
        joinedload(DBSession.mentor),
        selectinload(DBSession.student),
        selectinload(DBSession.payments)
    )

    # Filter by status if provided
    if status:
        query = query.filter(DBSession.status == status)

    return query.order_by(DBSession.scheduled_at.desc()).all()


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mentor_id: int | None = Depends(get_current_user_mentor_id),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить информацию о сессии по ID"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    # Проверка доступа: студент, ментор или админ
    if (session.student_id != current_user.id and
        session.mentor_id != mentor_id and
        current_user.role.value != "admin"):
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    return session


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Создать сессию (только для менторов и администраторов)"""
    # Проверяем что пользователь ментор или админ
    if current_user.role.value not in ["mentor", "admin"]:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Требуются права ментора.")

    # Санитизация входных данных
    try:
        sanitized_meeting_link = sanitize_and_validate(session.meeting_link, field_name="ссылке на встречу") if session.meeting_link else None
        sanitized_notes = sanitize_and_validate(session.notes, field_name="заметках") if session.notes else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Проверяем, что студент и ментор существуют одним запросом (N+1 fix)
    user_ids = {session.student_id, session.mentor_id}
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {u.id: u for u in users}

    if session.student_id not in user_map:
        raise HTTPException(status_code=404, detail="Студент не найден")

    # Один запрос вместо двух: находим ментора сессии И ментора текущего пользователя
    mentors = db.query(Mentor).filter(
        or_(Mentor.id == session.mentor_id, Mentor.user_id == current_user.id)
    ).all()
    mentor_map = {m.id: m for m in mentors}

    session_mentor = mentor_map.get(session.mentor_id)
    if not session_mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")

    # Если пользователь не админ, проверяем что он создаёт сессию как ментор
    if current_user.role.value != "admin" and session.mentor_id != current_user.id:
        # Находим mentor profile текущего пользователя
        user_mentor_profile = next((m for m in mentors if m.user_id == current_user.id), None)
        if not user_mentor_profile or user_mentor_profile.id != session.mentor_id:
            raise HTTPException(status_code=403, detail="Вы можете создавать сессии только от своего имени")

    # Создаем сессию с санитизированными данными
    db_session = DBSession(
        student_id=session.student_id,
        mentor_id=session.mentor_id,
        scheduled_at=session.scheduled_at,
        duration_minutes=session.duration_minutes,
        meeting_link=sanitized_meeting_link,
        notes=sanitized_notes,
    )
    db.add(db_session)

    try:
        db.commit()
        db.refresh(db_session)
        return db_session
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании сессии") from e


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mentor_id: int | None = Depends(get_current_user_mentor_id),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить сессию (только для участников сессии или администратора)"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    # Проверка ownership: студент, ментор или админ
    if (db_session.student_id != current_user.id and
        db_session.mentor_id != mentor_id and
        current_user.role.value != "admin"):
        raise HTTPException(status_code=403, detail="Доступ запрещен. Вы не участник этой сессии.")

    # Санитизация входных данных
    sanitized_data = {}
    for key, value in session.model_dump(exclude_unset=True).items():
        if key in ["meeting_link", "notes"] and value is not None:
            try:
                field_name = "ссылке на встречу" if key == "meeting_link" else "заметках"
                sanitized_data[key] = sanitize_and_validate(value, field_name=field_name)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        else:
            sanitized_data[key] = value

    # Обновляем поля
    for key, value in sanitized_data.items():
        setattr(db_session, key, value)

    try:
        db.commit()
        db.refresh(db_session)
        return db_session
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating session: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении сессии") from e


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mentor_id: int | None = Depends(get_current_user_mentor_id),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Удалить сессию (только для участников сессии или администратора)"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    # Проверка ownership: студент, ментор или админ
    if (db_session.student_id != current_user.id and
        db_session.mentor_id != mentor_id and
        current_user.role.value != "admin"):
        raise HTTPException(status_code=403, detail="Доступ запрещен. Вы не участник этой сессии.")

    try:
        db.delete(db_session)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении сессии") from e
