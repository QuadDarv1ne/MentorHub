"""
Video Calls Agora Integration
Интеграция с Agora SDK для видеозвонков
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, rate_limit_dependency
from app.models.user import User
from app.models.video_call import VideoCall
from app.schemas.video_call import AgoraTokenResponse
from app.services.agora_service import agora_service

router = APIRouter()


@router.post("/{call_id}/join", response_model=AgoraTokenResponse)
async def join_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Присоединиться к видеозвонку (получить Agora токен)"""
    call = db.query(VideoCall).filter(VideoCall.id == call_id).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Видеозвонок не найден"
        )

    # Проверяем права доступа
    from app.models.session import Session as SessionModel
    session = db.query(SessionModel).filter(SessionModel.id == call.session_id).first()

    if current_user.id not in [session.student_id, session.mentor_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для присоединения к звонку"
        )

    # Проверяем статус звонка
    if call.status not in ["scheduled", "active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Звонок недоступен для присоединения"
        )

    # Генерируем Agora токен
    try:
        is_host = (current_user.id == session.mentor_id)
        token_data = agora_service.generate_token_for_call(
            call_id=call.id,
            user_id=current_user.id,
            is_host=is_host
        )

        return AgoraTokenResponse(**token_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@router.post("/{call_id}/start", response_model=dict)
async def start_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Начать видеозвонок"""
    call = db.query(VideoCall).filter(VideoCall.id == call_id).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Видеозвонок не найден"
        )

    # Проверяем права (только ментор может начать звонок)
    from app.models.session import Session as SessionModel
    session = db.query(SessionModel).filter(SessionModel.id == call.session_id).first()

    if current_user.id != session.mentor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только ментор может начать звонок"
        )

    # Проверяем статус
    if call.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Звонок уже начат или завершен"
        )

    # Обновляем статус
    call.status = "active"
    call.started_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Звонок начат", "call_id": call.id, "status": call.status}


@router.post("/{call_id}/end", response_model=dict)
async def end_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Завершить видеозвонок"""
    call = db.query(VideoCall).filter(VideoCall.id == call_id).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Видеозвонок не найден"
        )

    # Проверяем права
    from app.models.session import Session as SessionModel
    session = db.query(SessionModel).filter(SessionModel.id == call.session_id).first()

    if current_user.id not in [session.student_id, session.mentor_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для завершения звонка"
        )

    # Проверяем статус
    if call.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Звонок не активен"
        )

    # Обновляем статус
    call.status = "ended"
    call.ended_at = datetime.now(timezone.utc)

    # Вычисляем длительность
    if call.started_at:
        duration = (call.ended_at - call.started_at).total_seconds() / 60
        call.duration_minutes = int(duration)

    db.commit()

    return {
        "message": "Звонок завершен",
        "call_id": call.id,
        "status": call.status,
        "duration_minutes": call.duration_minutes
    }


@router.get("/{call_id}/recording-config", response_model=dict)
async def get_recording_config(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить конфигурацию записи для видеозвонка"""
    call = db.query(VideoCall).filter(VideoCall.id == call_id).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Видеозвонок не найден"
        )

    # Проверяем права
    from app.models.session import Session as SessionModel
    session = db.query(SessionModel).filter(SessionModel.id == call.session_id).first()

    if current_user.id not in [session.student_id, session.mentor_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    # Получаем конфигурацию записи
    return agora_service.get_recording_config(call.id)
