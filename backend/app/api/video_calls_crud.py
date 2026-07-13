"""
Video Calls CRUD Operations
Базовые CRUD операции для видеозвонков
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db, rate_limit_dependency
from app.models.user import User
from app.models.video_call import CallStatus, VideoCall
from app.schemas.video_call import VideoCallCreate, VideoCallListResponse, VideoCallResponse

router = APIRouter()


def _format_call_response(call: VideoCall) -> dict[str, Any]:
    """Форматирование ответа для видеозвонка"""
    return {
        "id": call.id,
        "session_id": call.session_id,
        "creator_id": call.creator_id,
        "creator_username": call.creator.username if call.creator else None,
        "participant_id": call.participant_id,
        "participant_username": call.participant.username if call.participant else None,
        "call_type": call.call_type.value if call.call_type else "one_on_one",
        "room_id": call.room_id,
        "agora_channel": call.agora_channel,
        "agora_token": call.agora_token,
        "status": call.status.value if call.status else None,
        "scheduled_at": call.scheduled_at,
        "started_at": call.started_at,
        "ended_at": call.ended_at,
        "duration_seconds": call.duration_seconds,
        "title": call.title,
        "description": call.description,
        "created_at": call.created_at,
        "updated_at": call.updated_at,
    }


@router.post("/", response_model=VideoCallResponse, status_code=status.HTTP_201_CREATED)
async def create_video_call(
    call_data: VideoCallCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Создать видеозвонок"""
    from app.models.session import Session as SessionModel
    session = db.query(SessionModel).filter(SessionModel.id == call_data.session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )

    # Проверяем права (только участники сессии могут создавать звонок)
    if current_user.id not in [session.student_id, session.mentor_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания звонка"
        )

    # Проверяем, нет ли уже активного звонка для этой сессии
    existing_call = (
        db.query(VideoCall)
        .filter(
            VideoCall.session_id == call_data.session_id,
            VideoCall.status.in_(["scheduled", CallStatus.IN_PROGRESS.value])
        )
        .first()
    )

    if existing_call:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Для этой сессии уже существует активный звонок"
        )

    # Создаем звонок
    agora_channel = f"call_{call_data.session_id}_{int(datetime.now(timezone.utc).timestamp())}"

    video_call = VideoCall(
        session_id=call_data.session_id,
        creator_id=current_user.id,
        participant_id=session.mentor_id if current_user.id != session.mentor_id else session.student_id,
        agora_channel=agora_channel,
        status=CallStatus.SCHEDULED,
    )

    db.add(video_call)
    db.commit()
    db.refresh(video_call)

    # Загружаем связи
    refreshed_call = (
        db.query(VideoCall)
        .options(joinedload(VideoCall.creator), joinedload(VideoCall.participant))
        .filter(VideoCall.id == video_call.id)
        .first()
    )

    if not refreshed_call:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось загрузить созданный звонок"
        )

    return _format_call_response(refreshed_call)


@router.get("/", response_model=VideoCallListResponse)
async def get_video_calls(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str = Query(None, description="Фильтр по статусу: scheduled, active, ended, cancelled"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить список видеозвонков пользователя"""
    from app.models.session import Session as SessionModel

    # Получаем сессии пользователя
    user_sessions = (
        db.query(SessionModel.id)
        .filter(
            (SessionModel.student_id == current_user.id) |
            (SessionModel.mentor_id == current_user.id)
        )
        .all()
    )

    session_ids = [s.id for s in user_sessions]

    # Базовый запрос
    query = (
        db.query(VideoCall)
        .options(joinedload(VideoCall.creator), joinedload(VideoCall.participant))
        .filter(VideoCall.session_id.in_(session_ids))
    )

    # Фильтр по статусу
    if status:
        query = query.filter(VideoCall.status == status)

    # Подсчет общего количества
    total = query.count()

    # Пагинация
    calls = (
        query
        .order_by(VideoCall.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "items": [_format_call_response(call) for call in calls],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{call_id}", response_model=VideoCallResponse)
async def get_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить информацию о видеозвонке"""
    call = (
        db.query(VideoCall)
        .options(joinedload(VideoCall.creator), joinedload(VideoCall.participant))
        .filter(VideoCall.id == call_id)
        .first()
    )

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Видеозвонок не найден"
        )

    # Проверяем права доступа
    from app.models.session import Session as SessionModel
    session = db.query(SessionModel).filter(SessionModel.id == call.session_id).first()

    if not session or current_user.id not in [session.student_id, session.mentor_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра звонка"
        )

    return _format_call_response(call)


@router.delete("/{call_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Отменить видеозвонок"""
    call = (
        db.query(VideoCall)
        .options(joinedload(VideoCall.creator), joinedload(VideoCall.participant))
        .filter(VideoCall.id == call_id)
        .first()
    )

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Видеозвонок не найден"
        )

    # Проверяем права
    from app.models.session import Session as SessionModel
    session = db.query(SessionModel).filter(SessionModel.id == call.session_id).first()

    if not session or current_user.id not in [session.student_id, session.mentor_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для отмены звонка"
        )

    # Можно отменить только запланированные звонки
    if call.status not in [CallStatus.SCHEDULED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно отменить только запланированные звонки"
        )

    call.status = CallStatus.CANCELLED.value
    db.commit()

    return None
