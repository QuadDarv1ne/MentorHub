"""
Chat rooms API endpoints
Групповые чаты для курсов и проектов
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from datetime import datetime, timezone

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.chat_room import ChatRoom, ChatMessage, chat_room_members
from app.schemas.chat_room import (
    ChatRoomCreate, ChatRoomUpdate, ChatRoomResponse, ChatRoomWithMembersResponse,
    ChatMessageCreate, ChatMessageResponse, ChatMessageListResponse, AddMemberRequest, RemoveMemberRequest
)

router = APIRouter()


@router.post("/chat-rooms", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_room(
    chat_room: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать чат-комнату"""
    db_room = ChatRoom(
        name=chat_room.name,
        description=chat_room.description,
        created_by=current_user.id,
        is_private=chat_room.is_private,
        course_id=chat_room.course_id
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    
    # Добавляем создателя как участника
    db_room.members.append(current_user)
    db.commit()
    db.refresh(db_room)
    
    return db_room


@router.get("/chat-rooms", response_model=List[ChatRoomResponse])
async def get_chat_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список чат-комнат, где пользователь является участником"""
    query = db.query(ChatRoom).filter(
        ChatRoom.members.any(User.id == current_user.id)
    ).options(
        joinedload(ChatRoom.creator)
    ).order_by(desc(ChatRoom.updated_at))
    
    total = query.count()
    rooms = query.offset(skip).limit(limit).all()
    
    result = []
    for room in rooms:
        member_count = db.query(func.count(chat_room_members.c.user_id)).filter(
            chat_room_members.c.chat_room_id == room.id
        ).scalar()
        
        result.append({
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "created_by": room.created_by,
            "is_private": room.is_private,
            "course_id": room.course_id,
            "created_at": room.created_at,
            "updated_at": room.updated_at,
            "member_count": member_count
        })
    
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
    query = db.query(ChatMessage).filter(
        ChatMessage.room_id == room_id,
        ChatMessage.is_deleted == False
    ).options(
        joinedload(ChatMessage.sender)
    ).order_by(desc(ChatMessage.created_at))
    
    total = query.count()
    messages = query.offset(skip).limit(limit).all()
    
    # Переворачиваем для хронологического порядка
    messages.reverse()
    
    # Считаем количество ответов для каждого сообщения
    result = []
    for msg in messages:
        replies_count = db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.parent_message_id == msg.id
        ).scalar()
        
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
            "replies_count": replies_count
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
    
    db_message = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=message.content,
        attachment_url=message.attachment_url,
        attachment_type=message.attachment_type,
        parent_message_id=message.parent_message_id
    )
    db.add(db_message)
    
    # Обновляем updated_at у комнаты
    room.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_message)
    
    # Получаем данные отправителя
    sender = db.query(User).filter(User.id == current_user.id).first()
    
    return {
        "id": db_message.id,
        "room_id": db_message.room_id,
        "sender_id": db_message.sender_id,
        "sender_username": sender.username,
        "sender_avatar": sender.avatar_url,
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
    
    db_message.content = message_data.content
    db_message.is_edited = True
    db_message.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_message)
    
    sender = db.query(User).filter(User.id == current_user.id).first()
    
    return {
        "id": db_message.id,
        "room_id": db_message.room_id,
        "sender_id": db_message.sender_id,
        "sender_username": sender.username,
        "sender_avatar": sender.avatar_url,
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
