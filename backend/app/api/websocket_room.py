"""
WebSocket Group Chat Room Endpoint

Multi-user chat rooms.
"""

import logging
from datetime import datetime, timezone

from fastapi import Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.api.websocket_manager import manager
from app.dependencies import get_db
from app.models.chat_room import ChatMessage, ChatRoom
from app.models.user import User

logger = logging.getLogger(__name__)


async def authenticate_and_join_room(
    websocket: WebSocket,
    room_id: int,
    token: str,
    db: Session
) -> tuple[User, ChatRoom]:
    """Authenticate user and join room."""
    # Authenticate
    from app.utils.security import decode_access_token

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise ValueError("User not found")

    # Check room membership
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.members.any(User.id == user.id)
    ).first()

    if not room:
        raise ValueError("Room not found or not a member")

    return user, room


async def handle_room_message(
    websocket: WebSocket,
    data: dict,
    user: User,
    room_id: int,
    db: Session
):
    """Handle group chat message."""
    content = data.get("content", "").strip()
    attachment_url = data.get("attachment_url")
    attachment_type = data.get("attachment_type")
    parent_message_id = data.get("parent_message_id")

    if not content and not attachment_url:
        await websocket.send_json({
            "type": "error",
            "message": "Message must have content or attachment"
        })
        return

    # Save message
    chat_message = ChatMessage(
        room_id=room_id,
        sender_id=user.id,
        content=content,
        attachment_url=attachment_url,
        attachment_type=attachment_type,
        parent_message_id=parent_message_id
    )
    db.add(chat_message)

    # Update room updated_at
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if room:
        room.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(chat_message)

    # Format response
    message_data = {
        "type": "message",
        "id": chat_message.id,
        "room_id": room_id,
        "sender_id": user.id,
        "sender_username": user.username,
        "sender_avatar": user.avatar_url,
        "content": content,
        "attachment_url": attachment_url,
        "attachment_type": attachment_type,
        "parent_message_id": parent_message_id,
        "is_edited": False,
        "is_deleted": False,
        "timestamp": chat_message.created_at.isoformat()
    }

    # Send to sender and all room members
    await websocket.send_json(message_data)
    await manager.broadcast_to_room(room_id, message_data, exclude_user_id=user.id)

    logger.info(f"📨 Room message {chat_message.id} in room {room_id} from {user.id}")


async def handle_room_typing(
    data: dict,
    user: User,
    room_id: int
):
    """Handle typing indicator in room."""
    await manager.broadcast_to_room(room_id, {
        "type": "typing",
        "user_id": user.id,
        "username": user.username
    }, exclude_user_id=user.id)


async def websocket_room_handler(
    room_id: int,
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket handler for group chat room.

    Authentication: send token in first message:
    {"type": "auth", "token": "your_jwt_token"}
    """
    user = None
    room = None

    try:
        # Get token from first message
        data = await websocket.receive_json()

        if data.get("type") != "auth":
            await websocket.send_json({"type": "error", "message": "First message must be auth type"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        token = data.get("token")
        if not token:
            await websocket.send_json({"type": "error", "message": "Missing token"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Authenticate and join room
        authenticated_user, room = await authenticate_and_join_room(websocket, room_id, token, db)

        # Connect and join room
        await manager.connect(websocket, authenticated_user.id)
        await manager.join_room(room_id, authenticated_user.id)

        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "user_id": authenticated_user.id,
            "username": authenticated_user.username,
            "room_id": room_id,
            "room_name": room.name,
            "online_members": manager.get_room_online_members(room_id)
        })

        # Notify others about user joining
        await manager.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": authenticated_user.id,
            "username": authenticated_user.username
        }, exclude_user_id=authenticated_user.id)

        # Main message loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "message":
                await handle_room_message(websocket, data, authenticated_user, room_id, db)

            elif message_type == "typing":
                await handle_room_typing(data, authenticated_user, room_id)

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        if user:
            await manager.leave_room(room_id, user.id)
            manager.disconnect(websocket, user.id)

            # Notify others about user leaving
            await manager.broadcast_to_room(room_id, {
                "type": "user_left",
                "user_id": user.id,
                "username": user.username
            })

            logger.info(f"User {user.id} disconnected from room {room_id}")

    except Exception as e:
        logger.error(f"WebSocket room error: {e}")
        if user:
            try:
                await manager.leave_room(room_id, user.id)
            except Exception as leave_error:
                logger.error(f"Failed to leave room: {leave_error}")
            manager.disconnect(websocket, user.id)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception as close_error:
            logger.debug(f"Failed to close websocket: {close_error}")
