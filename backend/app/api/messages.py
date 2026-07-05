"""
Роуты сообщений
API для работы с сообщениями между пользователями
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, rate_limit_dependency
from app.models.message import Message as DBMessage
from app.models.user import User
from app.schemas.message import ConversationResponse, MessageCreate, MessageListResponse, MessageResponse, MessageUpdate
from app.utils.sanitization import sanitize_and_validate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список всех диалогов текущего пользователя с последними сообщениями"""
    # Подзапрос: определяем собеседника для каждого сообщения
    other_user = func.case(
        (DBMessage.sender_id == current_user.id, DBMessage.recipient_id),
        else_=DBMessage.sender_id,
    ).label("other_user_id")

    # Подзапрос: последнее сообщение в каждом диалоге
    last_msg_subq = (
        db.query(
            other_user.label("other_user_id"),
            DBMessage.content.label("last_message"),
            DBMessage.created_at.label("last_message_time"),
            DBMessage.sender_id.label("last_sender_id"),
        )
        .filter(
            or_(
                DBMessage.sender_id == current_user.id,
                DBMessage.recipient_id == current_user.id,
            )
        )
        .order_by(DBMessage.created_at.desc())
        .subquery()
    )

    # Подзапрос: количество непрочитанных сообщений от каждого собеседника
    unread_subq = (
        db.query(
            DBMessage.sender_id.label("other_user_id"),
            func.count().label("unread_count"),
        )
        .filter(
            DBMessage.recipient_id == current_user.id,
            DBMessage.is_read == False,
        )
        .group_by(DBMessage.sender_id)
        .subquery()
    )

    # Основной запрос: объединяем последнее сообщение + непрочитанные + данные пользователя
    rows = (
        db.query(
            last_msg_subq.c.other_user_id,
            last_msg_subq.c.last_message,
            last_msg_subq.c.last_message_time,
            last_msg_subq.c.last_sender_id,
            User.username,
            User.avatar_url,
            func.coalesce(unread_subq.c.unread_count, 0).label("unread_count"),
        )
        .join(User, User.id == last_msg_subq.c.other_user_id)
        .outerjoin(unread_subq, unread_subq.c.other_user_id == last_msg_subq.c.other_user_id)
        .order_by(last_msg_subq.c.last_message_time.desc())
        .all()
    )

    return [
        {
            "user_id": row.other_user_id,
            "username": row.username or f"User_{row.other_user_id}",
            "avatar_url": row.avatar_url,
            "last_message": row.last_message,
            "last_message_time": row.last_message_time,
            "unread_count": row.unread_count,
            "is_from_me": row.last_sender_id == current_user.id,
        }
        for row in rows
    ]


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
    # Проверяем существование собеседника
    other_user = db.query(User).filter(User.id == other_user_id).first()
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

    return db.query(DBMessage).offset(skip).limit(limit).all()


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

    # Санитизация и валидация входных данных
    try:
        sanitized_content = sanitize_and_validate(message.content, field_type="text", field_name="сообщении")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Проверяем, что получатель существует
    recipient = db.query(User).filter(User.id == message.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Получатель не найден")

    # Создаем сообщение с санитизированными данными
    try:
        db_message = DBMessage(sender_id=current_user.id, recipient_id=message.recipient_id, content=sanitized_content)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception:
        logger.exception("Failed to create message from user %s to %s", current_user.id, message.recipient_id)
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при отправке сообщения")


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

    # Санитизация и валидация входных данных
    sanitized_data = {}
    for key, value in message.model_dump(exclude_unset=True).items():
        if key == "content" and value is not None:
            try:
                sanitized_data[key] = sanitize_and_validate(value, field_type="text", field_name="сообщении")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        else:
            sanitized_data[key] = value

    # Обновляем поля
    for key, value in sanitized_data.items():
        setattr(db_message, key, value)

    try:
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception:
        logger.exception("Failed to update message %s by user %s", message_id, current_user.id)
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при обновлении сообщения")


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

    try:
        db.delete(db_message)
        db.commit()
        return None
    except Exception:
        logger.exception("Failed to delete message %s by user %s", message_id, current_user.id)
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при удалении сообщения")
