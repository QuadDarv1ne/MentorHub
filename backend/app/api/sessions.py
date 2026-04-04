"""
Роуты сессий
API для работы с сессиями менторства
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload

from app.dependencies import get_db, rate_limit_dependency, get_current_user
from app.models.session import Session as DBSession
from app.models.user import User
from app.models.mentor import Mentor
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.utils.sanitization import sanitize_string, is_safe_string

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[SessionResponse])
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
    
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100

    sessions = db.query(DBSession).options(
        joinedload(DBSession.mentor),
        joinedload(DBSession.student)
    ).offset(skip).limit(limit).all()
    return sessions


@router.get("/my", response_model=List[SessionResponse])
async def get_my_sessions(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить список сессий текущего пользователя (как студента или ментора)"""
    # Build query for sessions where user is either student or mentor
    query = db.query(DBSession).filter(
        (DBSession.student_id == current_user.id) | (DBSession.mentor_id == current_user.id)
    )

    # Join with mentor, student and payments to avoid N+1 problem
    query = query.options(
        joinedload(DBSession.mentor),
        joinedload(DBSession.student),
        selectinload(DBSession.payments)
    )

    # Filter by status if provided
    if status:
        query = query.filter(DBSession.status == status)

    sessions = query.order_by(DBSession.scheduled_at.desc()).all()
    return sessions


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить информацию о сессии по ID"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    # Проверка доступа: студент, ментор или админ
    if (session.student_id != current_user.id and 
        session.mentor_id != current_user.id and 
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
    sanitized_meeting_link = sanitize_string(session.meeting_link) if session.meeting_link else None
    sanitized_notes = sanitize_string(session.notes) if session.notes else None

    # Проверка на безопасность входных данных
    if sanitized_meeting_link and not is_safe_string(sanitized_meeting_link):
        raise HTTPException(status_code=400, detail="Недопустимые символы в ссылке на встречу")
    if sanitized_notes and not is_safe_string(sanitized_notes):
        raise HTTPException(status_code=400, detail="Недопустимые символы в заметках")

    # Проверяем, что студент и ментор существуют одним запросом (N+1 fix)
    user_ids = {session.student_id, session.mentor_id}
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {u.id: u for u in users}

    if session.student_id not in user_map:
        raise HTTPException(status_code=404, detail="Студент не найден")

    # Проверяем ментора через отдельный запрос (т.к. это другая таблица)
    mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")

    # Если пользователь не админ, проверяем что он создаёт сессию как ментор
    if current_user.role.value != "admin" and session.mentor_id != current_user.id:
        # Проверяем что пользователь associated с этим ментором
        user_mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
        if not user_mentor or user_mentor.id != session.mentor_id:
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
        raise HTTPException(status_code=500, detail="Ошибка при создании сессии")


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить сессию (только для участников сессии или администратора)"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    # Проверка ownership: студент, ментор или админ
    if (db_session.student_id != current_user.id and 
        db_session.mentor_id != current_user.id and 
        current_user.role.value != "admin"):
        raise HTTPException(status_code=403, detail="Доступ запрещен. Вы не участник этой сессии.")

    # Санитизация входных данных
    sanitized_data = {}
    for key, value in session.model_dump(exclude_unset=True).items():
        if key in ["meeting_link", "notes"] and value is not None:
            sanitized_value = sanitize_string(value)
            if not is_safe_string(sanitized_value):
                field_name = "ссылке на встречу" if key == "meeting_link" else "заметках"
                raise HTTPException(status_code=400, detail=f"Недопустимые символы в {field_name}")
            sanitized_data[key] = sanitized_value
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
        raise HTTPException(status_code=500, detail="Ошибка при обновлении сессии")


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Удалить сессию (только для участников сессии или администратора)"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    # Проверка ownership: студент, ментор или админ
    if (db_session.student_id != current_user.id and 
        db_session.mentor_id != current_user.id and 
        current_user.role.value != "admin"):
        raise HTTPException(status_code=403, detail="Доступ запрещен. Вы не участник этой сессии.")

    try:
        db.delete(db_session)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении сессии")
