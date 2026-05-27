"""
WebSocket 1-on-1 Chat Endpoint

Private messaging between users.
"""

import logging

from fastapi import Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.api.websocket_manager import manager
from app.dependencies import get_db
from app.models.message import Message
from app.models.notification import NotificationType
from app.models.user import User
from app.utils.security import decode_access_token

logger = logging.getLogger(__name__)


async def authenticate_websocket_user(
    token: str,
    db: Session
) -> User:
    """Authenticate user from WebSocket token."""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token")

        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise ValueError("User not found")

        return user
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        raise


async def handle_chat_message(
    websocket: WebSocket,
    data: dict,
    user: User,
    db: Session
):
    """Handle 1-on-1 chat message."""
    recipient_id = data.get("recipient_id")
    content = data.get("content", "").strip()

    if not recipient_id or not content:
        await websocket.send_json({
            "type": "error",
            "message": "Missing recipient_id or content"
        })
        return

    # Save message to database
    message = Message(
        sender_id=user.id,
        recipient_id=recipient_id,
        content=content,
        is_read=False
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    # Format response
    message_data = {
        "type": "message",
        "id": message.id,
        "sender_id": user.id,
        "sender_username": user.username,
        "sender_avatar": user.avatar_url,
        "recipient_id": recipient_id,
        "content": content,
        "timestamp": message.created_at.isoformat()
    }

    # Send confirmation to sender
    await websocket.send_json(message_data)

    # Send to recipient
    await manager.send_personal_message(message_data, recipient_id)

    # Real-time notification
    if manager.is_user_online(recipient_id):
        await manager.send_notification(recipient_id, {
            "notification_type": NotificationType.NEW_MESSAGE.value,
            "title": f"New message from {user.username}",
            "message": content[:100],
            "link": f"/messages/{user.id}"
        })

    logger.info(f"📨 Message {message.id} from {user.id} to {recipient_id}")


async def handle_typing_indicator(
    data: dict,
    user: User
):
    """Handle typing indicator."""
    recipient_id = data.get("recipient_id")
    if recipient_id:
        await manager.send_personal_message({
            "type": "typing",
            "user_id": user.id,
            "username": user.username
        }, recipient_id)


async def handle_read_receipt(
    data: dict,
    user: User,
    db: Session
):
    """Handle read receipt."""
    message_id = data.get("message_id")
    if not message_id:
        return

    message = db.query(Message).filter(
        Message.id == message_id,
        Message.recipient_id == user.id
    ).first()

    if message:
        message.is_read = True
        db.commit()

        # Notify sender
        await manager.send_personal_message({
            "type": "read",
            "message_id": message_id,
            "reader_id": user.id
        }, message.sender_id)


async def websocket_chat_handler(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket handler for 1-on-1 chat.
    
    Authentication: send token in first message:
    {"type": "auth", "token": "your_jwt_token"}
    """
    user = None
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

        # Authenticate
        user = await authenticate_websocket_user(token, db)

        # Connect
        await manager.connect(websocket, user.id)

        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "user_id": user.id,
            "username": user.username,
            "online_users": manager.get_online_users()
        })

        # Main message loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "message":
                await handle_chat_message(websocket, data, user, db)

            elif message_type == "typing":
                await handle_typing_indicator(data, user)

            elif message_type == "read":
                await handle_read_receipt(data, user, db)

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        if user:
            manager.disconnect(websocket, user.id)
            logger.info(f"User {user.id} disconnected normally")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user:
            manager.disconnect(websocket, user.id)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception as close_error:
            logger.debug(f"Failed to close websocket: {close_error}")
