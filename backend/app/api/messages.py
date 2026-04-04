"""
Роуты сообщений
API для работы с сообщениями между пользователями
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from datetime import datetime

from app.dependencies import get_db, rate_limit_dependency, get_current_user
from app.models.message import Message as DBMessage
from app.models.user import User
from app.schemas.message import MessageCreate, MessageUpdate, MessageResponse, MessageListResponse, ConversationResponse
from app.utils.sanitization import sanitize_text_field, is_safe_string

router = APIRouter()


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список всех диалогов текущего пользователя с последними сообщениями"""
    # Получаем все диалоги где пользователь участвует
    messages_query = db.query(
        DBMessage.sender_id,
        DBMessage.recipient_id,
        DBMessage.content,
        DBMessage.created_at,
        DBMessage.is_read
    ).filter(
        or_(
            DBMessage.sender_id == current_user.id,
            DBMessage.recipient_id == current_user.id
        )
    ).order_by(DBMessage.created_at.desc())

    # Группируем по собеседникам
    conversations = {}
    for msg in messages_query.all():
        other_user_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        if other_user_id not in conversations:
            conversations[other_user_id] = {
                "user_id": other_user_id,
                "last_message": msg.content,
                "last_message_time": msg.created_at,
                "unread_count": 0,
                "is_from_me": msg.sender_id == current_user.id
            }
        # Считаем непрочитанные
        if msg.sender_id != current_user.id and not msg.is_read:
            conversations[other_user_id]["unread_count"] += 1

    # Получаем данные пользователей
    user_ids = list(conversations.keys())
    users = db.query(User.id, User.username, User.avatar_url).filter(User.id.in_(user_ids)).all()
    users_dict = {u.id: {"username": u.username, "avatar_url": u.avatar_url} for u in users}

    # Формируем результат
    result = []
    for user_id, conv_data in conversations.items():
        user_info = users_dict.get(user_id, {"username": f"User_{user_id}", "avatar_url": None})
        result.append({
            "user_id": user_id,
            "username": user_info["username"],
            "avatar_url": user_info["avatar_url"],
            "last_message": conv_data["last_message"],
            "last_message_time": conv_data["last_message_time"],
            "unread_count": conv_data["unread_count"],
            "is_from_me": conv_data["is_from_me"]
        })

    # Сортируем по времени последнего сообщения
    result.sort(key=lambda x: x["last_message_time"], reverse=True)
    return result


@router.get("/history/{other_user_id}", response_model=MessageListResponse)
async def get_message_history(
    other_user_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    before: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить историю переписки с конкретным пользователем"""
    # Проверяем существование собеседника с использованием joinedload для оптимизации
    other_user = db.query(User).options(
        joinedload(User.sessions),
        joinedload(User.reviews)
    ).filter(User.id == other_user_id).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Строим запрос
    query = db.query(DBMessage).filter(
        or_(
            and_(DBMessage.sender_id == current_user.id, DBMessage.recipient_id == other_user_id),
            and_(DBMessage.sender_id == other_user_id, DBMessage.recipient_id == current_user.id)
        )
    )

    # Пагинация по времени
    if before:
        query = query.filter(DBMessage.created_at < before)

    # Получаем сообщения (последние сначала)
    messages = query.order_by(DBMessage.created_at.desc()).limit(limit).all()
    
    # Переворачиваем чтобы были в хронологическом порядке
    messages.reverse()

    # Помечаем сообщения как прочитанные
    unread_messages = db.query(DBMessage).filter(
        DBMessage.sender_id == other_user_id,
        DBMessage.recipient_id == current_user.id,
        DBMessage.is_read == False
    ).all()

    for msg in unread_messages:
        msg.is_read = True
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking messages as read: {e}")
        # Не прерываем запрос, просто логируем ошибку

    return {
        "messages": messages,
        "other_user": {
            "id": other_user.id,
            "username": other_user.username,
            "avatar_url": other_user.avatar_url
        },
        "has_more": len(messages) == limit
    }


@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список сообщений (admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    from app.utils.pagination import validate_pagination
    skip, limit = validate_pagination(skip, limit)

    messages = db.query(DBMessage).offset(skip).limit(limit).all()
    return messages


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить информацию о сообщении по ID"""
    # Пользователь может видеть только свои сообщения
    message = db.query(DBMessage).filter(
        DBMessage.id == message_id,
        or_(
            DBMessage.sender_id == current_user.id,
            DBMessage.recipient_id == current_user.id
        )
    ).first()

    # Администратор может видеть любые сообщения
    if not message and current_user.role.value == "admin":
        message = db.query(DBMessage).filter(DBMessage.id == message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    return message


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Создать сообщение"""
    # Пользователь может отправлять сообщения только от своего имени
    if message.sender_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Санитизация входных данных
    sanitized_content = sanitize_text_field(message.content)

    # Проверка на безопасность входных данных
    if not is_safe_string(sanitized_content):
        raise HTTPException(status_code=400, detail="Недопустимые символы в сообщении")

    # Проверяем, что получатель существует
    recipient = db.query(User).filter(User.id == message.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Получатель не найден")

    # Создаем сообщение с санитизированными данными
    db_message = DBMessage(sender_id=current_user.id, recipient_id=message.recipient_id, content=sanitized_content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    message: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить сообщение"""
    db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    # Только автор может редактировать своё сообщение (или админ)
    if db_message.sender_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    # Санитизация входных данных
    sanitized_data = {}
    for key, value in message.model_dump(exclude_unset=True).items():
        if key == "content" and value is not None:
            sanitized_value = sanitize_text_field(value)
            if not is_safe_string(sanitized_value):
                raise HTTPException(status_code=400, detail="Недопустимые символы в сообщении")
            sanitized_data[key] = sanitized_value
        else:
            sanitized_data[key] = value

    # Обновляем поля
    for key, value in sanitized_data.items():
        setattr(db_message, key, value)

    db.commit()
    db.refresh(db_message)
    return db_message


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Удалить сообщение"""
    db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    # Только автор может удалять своё сообщение (или админ)
    if db_message.sender_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    db.delete(db_message)
    db.commit()
    return None
