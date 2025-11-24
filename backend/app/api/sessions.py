"""
Роуты сессий
API для работы с сессиями менторства
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, rate_limit_dependency
from app.models.session import Session as DBSession
from app.models.user import User
from app.models.mentor import Mentor
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.utils.sanitization import sanitize_string, is_safe_string

router = APIRouter()


@router.get("/", response_model=List[SessionResponse])
async def get_sessions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список сессий"""
    # Проверка на корректность параметров пагинации
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100

    sessions = db.query(DBSession).offset(skip).limit(limit).all()
    return sessions


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить информацию о сессии по ID"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return session


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session: SessionCreate, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Создать сессию"""
    # Санитизация входных данных
    sanitized_meeting_link = sanitize_string(session.meeting_link) if session.meeting_link else None
    sanitized_notes = sanitize_string(session.notes) if session.notes else None

    # Проверка на безопасность входных данных
    if sanitized_meeting_link and not is_safe_string(sanitized_meeting_link):
        raise HTTPException(status_code=400, detail="Недопустимые символы в ссылке на встречу")
    if sanitized_notes and not is_safe_string(sanitized_notes):
        raise HTTPException(status_code=400, detail="Недопустимые символы в заметках")

    # Проверяем, что студент существует
    student = db.query(User).filter(User.id == session.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    # Проверяем, что ментор существует
    mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")

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
    db.commit()
    db.refresh(db_session)
    return db_session


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session: SessionUpdate,
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить сессию"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

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

    db.commit()
    db.refresh(db_session)
    return db_session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int, db: Session = Depends(get_db), rate_limit: bool = Depends(rate_limit_dependency)
):
    """Удалить сессию"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    db.delete(db_session)
    db.commit()
    return None
