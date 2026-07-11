"""
Chat rooms API endpoints
Групповые чаты для курсов и проектов
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db
from app.models.chat_room import ChatMessage, ChatRoom
from app.models.user import User
from app.schemas.chat_room import (
    AddMemberRequest,
    ChatMessageCreate,
    ChatMessageListResponse,
    ChatMessageResponse,
    ChatMessageUpdate,
    ChatRoomCreate,
    ChatRoomResponse,
    ChatRoomWithMembersResponse,
)
from app.services.chat_room_service import ChatRoomService, format_room_response
from app.utils.sanitization import sanitize_and_validate

router = APIRouter()


def _get_chat_room_service(db: Session = Depends(get_db)) -> ChatRoomService:
    """Получить сервис чат-комнат"""
    return ChatRoomService(db)


@router.post("/chat-rooms", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_room(
    chat_room: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    service: ChatRoomService = Depends(_get_chat_room_service)
) -> ChatRoom:
    """Создать чат-комнату"""
    return service.create_chat_room(current_user, chat_room)


@router.get("/chat-rooms", response_model=list[ChatRoomResponse])
async def get_chat_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: ChatRoomService = Depends(_get_chat_room_service)
) -> list[dict[str, Any]]:
    """Получить список чат-комнат, где пользователь является участником"""
    rooms = service.get_user_rooms(current_user.id, skip, limit)

    result = []
    for room in rooms:
        member_count = service.get_room_member_count(room.id)
        result.append(format_room_response(room, member_count))

    return result


@router.get("/chat-rooms/{room_id}", response_model=ChatRoomWithMembersResponse)
async def get_chat_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о чат-комнате"""
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.members.any(User.id == current_user.id)
    ).options(
        joinedload(ChatRoom.creator),
        joinedload(ChatRoom.members)
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Чат не найден или вы не являетесь участником")

    members_data = []
    for member in room.members:
        members_data.append({
            "id": member.id,
            "username": member.username,
            "avatar_url": member.avatar_url,
            "role": member.role.value
        })

    return {
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "created_by": room.created_by,
        "is_private": room.is_private,
        "course_id": room.course_id,
        "created_at": room.created_at,
        "updated_at": room.updated_at,
        "member_count": len(room.members),
        "members": members_data,
        "creator_username": room.creator.username
    }


@router.post("/chat-rooms/{room_id}/members", status_code=status.HTTP_200_OK)
async def add_member_to_chat(
    room_id: int,
    member_data: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавить участника в чат"""
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.members.any(User.id == current_user.id)
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Чат не найден")

    # Проверка: только создатель может добавлять участников в приватный чат
    if room.is_private and room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Только создатель может добавлять участников в приватный чат")

    # Проверяем существует ли пользователь
    new_member = db.query(User).filter(User.id == member_data.user_id).first()
    if not new_member:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем, не является ли он уже участником
    if new_member in room.members:
        raise HTTPException(status_code=400, detail="Пользователь уже является участником чата")

    room.members.append(new_member)
    db.commit()

    return {"message": "Участник добавлен", "member_count": len(room.members)}


@router.delete("/chat-rooms/{room_id}/members/{user_id}", status_code=status.HTTP_200_OK)
async def remove_member_from_chat(
    room_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить участника из чата"""
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.members.any(User.id == current_user.id)
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Чат не найден")

    # Только создатель может удалять участников
    if room.created_by != current_user.id and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Только создатель может удалять участников")

    member_to_remove = db.query(User).filter(User.id == user_id).first()
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if member_to_remove not in room.members:
        raise HTTPException(status_code=400, detail="Пользователь не является участником чата")

    room.members.remove(member_to_remove)
    db.commit()

    return {"message": "Участник удалён", "member_count": len(room.members)}


@router.delete("/chat-rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить чат-комнату"""
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.created_by == current_user.id
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Чат не найден или у вас нет прав на удаление")

    db.delete(room)
    db.commit()

    return None


@router.get("/chat-rooms/{room_id}/messages", response_model=ChatMessageListResponse)
async def get_chat_messages(
    room_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить сообщения чата"""
    # Проверяем, что пользователь является участником
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.members.any(User.id == current_user.id)
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Чат не найден или вы не являетесь участником")

    # Получаем сообщения
    query = db.query(ChatMessage).options(
        joinedload(ChatMessage.sender)
    ).filter(
        ChatMessage.room_id == room_id,
        ChatMessage.is_deleted.is_(False)
    ).order_by(desc(ChatMessage.created_at))

    total = query.count()
    messages = query.offset(skip).limit(limit).all()

    # Переворачиваем для хронологического порядка
    messages.reverse()

    # Считаем количество ответов для каждого сообщения (один запрос вместо N+1)
    message_ids = [msg.id for msg in messages]
    replies_query = db.query(
        ChatMessage.parent_message_id,
        func.count(ChatMessage.id).label('replies_count')
    ).filter(
        ChatMessage.parent_message_id.in_(message_ids)
    ).group_by(ChatMessage.parent_message_id)

    replies_map = {row.parent_message_id: row.replies_count for row in replies_query}

    # Формируем ответ
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "room_id": msg.room_id,
            "sender_id": msg.sender_id,
            "sender_username": msg.sender.username,
            "sender_avatar": msg.sender.avatar_url,
            "content": msg.content,
            "is_edited": msg.is_edited,
            "is_deleted": msg.is_deleted,
            "attachment_url": msg.attachment_url,
            "attachment_type": msg.attachment_type,
            "parent_message_id": msg.parent_message_id,
            "created_at": msg.created_at,
            "updated_at": msg.updated_at,
            "replies_count": replies_map.get(msg.id, 0)
        })

    return {
        "messages": result,
        "has_more": skip + limit < total
    }


@router.post("/chat-rooms/{room_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    room_id: int,
    message: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправить сообщение в чат"""
    # Проверяем, что пользователь является участником
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.members.any(User.id == current_user.id)
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Чат не найден или вы не являетесь участником")

    # Проверяем родительское сообщение если это тред
    if message.parent_message_id:
        parent_msg = db.query(ChatMessage).filter(
            ChatMessage.id == message.parent_message_id,
            ChatMessage.room_id == room_id
        ).first()
        if not parent_msg:
            raise HTTPException(status_code=404, detail="Родительское сообщение не найдено")

    # Санитизация контента сообщения (XSS protection)
    try:
        sanitized_content = sanitize_and_validate(message.content, field_name="сообщении")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_message = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=sanitized_content,
        attachment_url=message.attachment_url,
        attachment_type=message.attachment_type,
        parent_message_id=message.parent_message_id
    )
    db.add(db_message)

    # Обновляем updated_at у комнаты
    room.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_message)

    return {
        "id": db_message.id,
        "room_id": db_message.room_id,
        "sender_id": db_message.sender_id,
        "sender_username": current_user.username,
        "sender_avatar": current_user.avatar_url,
        "content": db_message.content,
        "is_edited": db_message.is_edited,
        "is_deleted": db_message.is_deleted,
        "attachment_url": db_message.attachment_url,
        "attachment_type": db_message.attachment_type,
        "parent_message_id": db_message.parent_message_id,
        "created_at": db_message.created_at,
        "updated_at": db_message.updated_at,
        "replies_count": 0
    }


@router.put("/chat-messages/{message_id}", response_model=ChatMessageResponse)
async def edit_chat_message(
    message_id: int,
    message_data: ChatMessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Редактировать сообщение"""
    db_message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.sender_id == current_user.id
    ).first()

    if not db_message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено или у вас нет прав на редактирование")

    if db_message.is_deleted:
        raise HTTPException(status_code=400, detail="Нельзя редактировать удалённое сообщение")

    # Санитизация нового контента (XSS protection)
    if message_data.content:
        try:
            db_message.content = sanitize_and_validate(message_data.content, field_name="сообщении")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    db_message.is_edited = True
    db_message.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_message)

    return {
        "id": db_message.id,
        "room_id": db_message.room_id,
        "sender_id": db_message.sender_id,
        "sender_username": current_user.username,
        "sender_avatar": current_user.avatar_url,
        "content": db_message.content,
        "is_edited": db_message.is_edited,
        "is_deleted": db_message.is_deleted,
        "attachment_url": db_message.attachment_url,
        "attachment_type": db_message.attachment_type,
        "parent_message_id": db_message.parent_message_id,
        "created_at": db_message.created_at,
        "updated_at": db_message.updated_at,
        "replies_count": 0
    }


@router.delete("/chat-messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить сообщение (soft delete)"""
    db_message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.sender_id == current_user.id
    ).first()

    if not db_message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено или у вас нет прав на удаление")

    db_message.is_deleted = True
    db_message.content = "[Сообщение удалено]"
    db_message.updated_at = datetime.now(timezone.utc)

    db.commit()

    return None
