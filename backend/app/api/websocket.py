"""
WebSocket API Router

Real-time communication endpoints:
- 1-on-1 chat
- Group chat rooms
- Online status
"""

import logging

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session

from app.api.websocket_chat import websocket_chat_handler
from app.api.websocket_manager import manager
from app.api.websocket_room import websocket_room_handler
from app.dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for 1-on-1 chat.
    
    Authentication: send token in first message:
    {"type": "auth", "token": "your_jwt_token"}
    
    Message types:
    - message: send private message
    - typing: typing indicator
    - read: read receipt
    - ping: keep-alive
    """
    await websocket_chat_handler(websocket, db)


@router.websocket("/ws/room/{room_id}")
async def websocket_room_endpoint(
    room_id: int,
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for group chat room.
    
    Authentication: send token in first message:
    {"type": "auth", "token": "your_jwt_token"}
    
    Message types:
    - message: send room message
    - typing: typing indicator
    - ping: keep-alive
    """
    await websocket_room_handler(room_id, websocket, db)


@router.get("/ws/online-users")
async def get_online_users():
    """Get list of online users."""
    return {
        "online_users": manager.get_online_users(),
        "count": len(manager.get_online_users())
    }


@router.get("/ws/room/{room_id}/online")
async def get_room_online_members(room_id: int):
    """Get online room members."""
    return {
        "room_id": room_id,
        "online_members": manager.get_room_online_members(room_id),
        "count": len(manager.get_room_online_members(room_id))
    }
