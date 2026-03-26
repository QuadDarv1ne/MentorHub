"""
Video Calls API
Интеграция с Agora для видеозвонков
"""

import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.video_call import VideoCall, CallType, CallStatus
from app.models.chat_room import ChatRoom
from app.schemas.video_call import (
    VideoCallCreate, VideoCallUpdate, VideoCallResponse, 
    VideoCallListResponse, AgoraTokenResponse
)

router = APIRouter(prefix="/calls", tags=["Video Calls"])


# Agora конфигурация
AGORA_APP_ID = os.getenv("AGORA_APP_ID", "")
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE", "")

try:
    from agora_token_builder import RtcTokenBuilder, RtcTokenBuilderRole
    AGORA_AVAILABLE = True
except ImportError:
    AGORA_AVAILABLE = False


def generate_agora_token(channel: str, uid: int, role: str = "publisher", expiration: int = 3600) -> str:
    """Генерация токена Agora"""
    if not AGORA_AVAILABLE or not AGORA_APP_ID or not AGORA_APP_CERTIFICATE:
        return ""
    
    try:
        current_time = datetime.now(timezone.utc)
        privilege_expired_ts = int((current_time + timedelta(seconds=expiration)).timestamp())
        
        if role == "publisher":
            rtc_role = RtcTokenBuilderRole.PUBLISHER
        else:
            rtc_role = RtcTokenBuilderRole.SUBSCRIBER
        
        token = RtcTokenBuilder.build_token_with_uid(
            AGORA_APP_ID,
            AGORA_APP_CERTIFICATE,
            channel,
            uid,
            rtc_role,
            privilege_expired_ts
        )
        return token
    except Exception as e:
        return ""


@router.post("/", response_model=VideoCallResponse, status_code=status.HTTP_201_CREATED)
async def create_video_call(
    call_data: VideoCallCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать видеозвонок"""

    # Определяем тип звонка с использованием joinedload (N+1 fix)
    if call_data.room_id:
        call_type = CallType.GROUP
        # Проверяем, что пользователь является участником комнаты
        room = db.query(ChatRoom).options(
            joinedload(ChatRoom.members)
        ).filter(
            ChatRoom.id == call_data.room_id,
            ChatRoom.members.any(User.id == current_user.id)
        ).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found or you are not a member")
    elif call_data.participant_id:
        call_type = CallType.ONE_ON_ONE
        # Проверяем существование участника
        participant = db.query(User).filter(User.id == call_data.participant_id).first()
        if not participant:
            raise HTTPException(status_code=404, detail="Participant not found")
    else:
        raise HTTPException(status_code=400, detail="Either participant_id or room_id must be provided")
    
    # Генерируем уникальный канал
    agora_channel = f"call_{uuid.uuid4().hex[:12]}"
    
    # Создаем звонок
    video_call = VideoCall(
        creator_id=current_user.id,
        call_type=call_type,
        participant_id=call_data.participant_id,
        room_id=call_data.room_id,
        agora_channel=agora_channel,
        status=CallStatus.SCHEDULED if call_data.scheduled_at else CallStatus.SCHEDULED,
        scheduled_at=call_data.scheduled_at,
        title=call_data.title,
        description=call_data.description
    )
    
    db.add(video_call)
    db.commit()
    db.refresh(video_call)
    
    # Генерируем токен
    agora_token = generate_agora_token(agora_channel, current_user.id)
    video_call.agora_token = agora_token
    
    db.commit()
    db.refresh(video_call)

    # Формируем ответ с использованием joinedload (N+1 fix)
    # Получаем все данные одним запросом через relationship
    return {
        "id": video_call.id,
        "creator_id": video_call.creator_id,
        "creator_username": video_call.creator.username if video_call.creator else None,
        "participant_id": video_call.participant_id,
        "participant_username": video_call.participant.username if video_call.participant else None,
        "call_type": video_call.call_type.value,
        "room_id": video_call.room_id,
        "room_name": video_call.room.name if video_call.room else None,
        "agora_channel": video_call.agora_channel,
        "agora_token": video_call.agora_token,
        "agora_app_id": AGORA_APP_ID,
        "status": video_call.status.value,
        "scheduled_at": video_call.scheduled_at,
        "started_at": video_call.started_at,
        "ended_at": video_call.ended_at,
        "duration_seconds": video_call.duration_seconds,
        "title": video_call.title,
        "description": video_call.description,
        "created_at": video_call.created_at,
        "updated_at": video_call.updated_at
    }


@router.get("/", response_model=VideoCallListResponse)
async def get_video_calls(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список видеозвонков пользователя"""
    
    # Звонки где пользователь создатель или участник
    query = db.query(VideoCall).filter(
        or_(
            VideoCall.creator_id == current_user.id,
            VideoCall.participant_id == current_user.id,
            VideoCall.room_id.in_(
                db.query(ChatRoom.id).filter(
                    ChatRoom.members.any(User.id == current_user.id)
                )
            )
        )
    ).options(
        joinedload(VideoCall.creator),
        joinedload(VideoCall.participant),
        joinedload(VideoCall.chat_room)
    ).order_by(desc(VideoCall.created_at))
    
    # Фильтр по статусу
    if status_filter:
        try:
            call_status = CallStatus(status_filter)
            query = query.filter(VideoCall.status == call_status)
        except ValueError:
            pass
    
    total = query.count()
    calls = query.offset(skip).limit(limit).all()
    
    # Формируем ответ
    result = []
    for call in calls:
        result.append({
            "id": call.id,
            "creator_id": call.creator_id,
            "creator_username": call.creator.username if call.creator else None,
            "participant_id": call.participant_id,
            "participant_username": call.participant.username if call.participant else None,
            "call_type": call.call_type.value,
            "room_id": call.room_id,
            "room_name": call.chat_room.name if call.chat_room else None,
            "agora_channel": call.agora_channel,
            "agora_token": call.agora_token,
            "agora_app_id": AGORA_APP_ID,
            "status": call.status.value,
            "scheduled_at": call.scheduled_at,
            "started_at": call.started_at,
            "ended_at": call.ended_at,
            "duration_seconds": call.duration_seconds,
            "title": call.title,
            "description": call.description,
            "created_at": call.created_at,
            "updated_at": call.updated_at
        })
    
    return {"calls": result, "total": total}


@router.get("/{call_id}", response_model=VideoCallResponse)
async def get_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о видеозвонке"""
    
    call = db.query(VideoCall).filter(
        VideoCall.id == call_id,
        or_(
            VideoCall.creator_id == current_user.id,
            VideoCall.participant_id == current_user.id,
            VideoCall.room_id.in_(
                db.query(ChatRoom.id).filter(
                    ChatRoom.members.any(User.id == current_user.id)
                )
            )
        )
    ).options(
        joinedload(VideoCall.creator),
        joinedload(VideoCall.participant),
        joinedload(VideoCall.chat_room)
    ).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found or access denied")
    
    return {
        "id": call.id,
        "creator_id": call.creator_id,
        "creator_username": call.creator.username if call.creator else None,
        "participant_id": call.participant_id,
        "participant_username": call.participant.username if call.participant else None,
        "call_type": call.call_type.value,
        "room_id": call.room_id,
        "room_name": call.chat_room.name if call.chat_room else None,
        "agora_channel": call.agora_channel,
        "agora_token": call.agora_token,
        "agora_app_id": AGORA_APP_ID,
        "status": call.status.value,
        "scheduled_at": call.scheduled_at,
        "started_at": call.started_at,
        "ended_at": call.ended_at,
        "duration_seconds": call.duration_seconds,
        "title": call.title,
        "description": call.description,
        "created_at": call.created_at,
        "updated_at": call.updated_at
    }


@router.post("/{call_id}/join", response_model=AgoraTokenResponse)
async def join_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить токен для подключения к звонку"""

    call = db.query(VideoCall).filter(
        VideoCall.id == call_id,
        or_(
            VideoCall.creator_id == current_user.id,
            VideoCall.participant_id == current_user.id,
            VideoCall.room_id.in_(
                db.query(ChatRoom.id).filter(
                    ChatRoom.members.any(User.id == current_user.id)
                )
            )
        )
    ).options(
        joinedload(VideoCall.creator),
        joinedload(VideoCall.participant),
        joinedload(VideoCall.chat_room)
    ).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found or access denied")

    # Генерируем токен
    agora_token = generate_agora_token(call.agora_channel, current_user.id)

    return {
        "agora_app_id": AGORA_APP_ID,
        "agora_channel": call.agora_channel,
        "agora_token": agora_token
    }


@router.post("/{call_id}/start", response_model=VideoCallResponse)
async def start_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Начать видеозвонок"""

    call = db.query(VideoCall).filter(
        VideoCall.id == call_id,
        VideoCall.creator_id == current_user.id
    ).options(
        joinedload(VideoCall.creator),
        joinedload(VideoCall.participant),
        joinedload(VideoCall.chat_room)
    ).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found or you are not the creator")

    call.status = CallStatus.IN_PROGRESS
    call.started_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(call)

    # Используем loaded relationships (N+1 fix)
    return {
        "id": call.id,
        "creator_id": call.creator_id,
        "creator_username": call.creator.username if call.creator else None,
        "participant_id": call.participant_id,
        "participant_username": call.participant.username if call.participant else None,
        "call_type": call.call_type.value,
        "room_id": call.room_id,
        "room_name": call.chat_room.name if call.chat_room else None,
        "agora_channel": call.agora_channel,
        "agora_token": call.agora_token,
        "agora_app_id": AGORA_APP_ID,
        "status": call.status.value,
        "scheduled_at": call.scheduled_at,
        "started_at": call.started_at,
        "ended_at": call.ended_at,
        "duration_seconds": call.duration_seconds,
        "title": call.title,
        "description": call.description,
        "created_at": call.created_at,
        "updated_at": call.updated_at
    }


@router.post("/{call_id}/end", response_model=VideoCallResponse)
async def end_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Завершить видеозвонок"""

    call = db.query(VideoCall).filter(
        VideoCall.id == call_id,
        or_(
            VideoCall.creator_id == current_user.id,
            VideoCall.participant_id == current_user.id
        )
    ).options(
        joinedload(VideoCall.creator),
        joinedload(VideoCall.participant),
        joinedload(VideoCall.chat_room)
    ).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found or access denied")

    call.status = CallStatus.COMPLETED
    call.ended_at = datetime.now(timezone.utc)

    if call.started_at:
        call.duration_seconds = int((call.ended_at - call.started_at).total_seconds())

    db.commit()
    db.refresh(call)

    # Используем loaded relationships (N+1 fix)
    return {
        "id": call.id,
        "creator_id": call.creator_id,
        "creator_username": call.creator.username if call.creator else None,
        "participant_id": call.participant_id,
        "participant_username": call.participant.username if call.participant else None,
        "call_type": call.call_type.value,
        "room_id": call.room_id,
        "room_name": call.chat_room.name if call.chat_room else None,
        "agora_channel": call.agora_channel,
        "agora_token": call.agora_token,
        "agora_app_id": AGORA_APP_ID,
        "status": call.status.value,
        "scheduled_at": call.scheduled_at,
        "started_at": call.started_at,
        "ended_at": call.ended_at,
        "duration_seconds": call.duration_seconds,
        "title": call.title,
        "description": call.description,
        "created_at": call.created_at,
        "updated_at": call.updated_at
    }


@router.delete("/{call_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_video_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отменить видеозвонок"""
    
    call = db.query(VideoCall).filter(
        VideoCall.id == call_id,
        VideoCall.creator_id == current_user.id
    ).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found or you are not the creator")
    
    if call.status == CallStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot cancel completed call")
    
    call.status = CallStatus.CANCELLED
    
    db.commit()
    
    return None
