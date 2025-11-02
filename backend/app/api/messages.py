"""
Роуты сообщений
API для работы с сообщениями между пользователями
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.message import Message as DBMessage
from app.models.user import User
from app.schemas.message import MessageCreate, MessageUpdate, MessageResponse

router = APIRouter()


@router.get("/", response_model=List[MessageResponse])
async def get_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список сообщений"""
    messages = db.query(DBMessage).offset(skip).limit(limit).all()
    return messages


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: int, db: Session = Depends(get_db)):
    """Получить информацию о сообщении по ID"""
    message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    return message


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """Создать сообщение"""
    # Проверяем, что отправитель существует
    sender = db.query(User).filter(User.id == message.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Отправитель не найден")
    
    # Проверяем, что получатель существует
    recipient = db.query(User).filter(User.id == message.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Получатель не найден")
    
    db_message = DBMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(message_id: int, message: MessageUpdate, db: Session = Depends(get_db)):
    """Обновить сообщение"""
    db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    
    for key, value in message.model_dump(exclude_unset=True).items():
        setattr(db_message, key, value)
    
    db.commit()
    db.refresh(db_message)
    return db_message


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(message_id: int, db: Session = Depends(get_db)):
    """Удалить сообщение"""
    db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    
    db.delete(db_message)
    db.commit()
    return None

