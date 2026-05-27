"""
WebSocket Connection Manager

Manages WebSocket connections, rooms, and message broadcasting.
"""

import logging
from typing import Dict, List, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager."""

    def __init__(self):
        # user_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # room_id -> set of user_ids
        self.room_members: Dict[int, Set[int]] = {}
        # user_id -> set of room_ids
        self.user_rooms: Dict[int, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect new client."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"✅ User {user_id} connected via WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect client."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"❌ User {user_id} disconnected from WebSocket")

    async def join_room(self, room_id: int, user_id: int):
        """User joins chat room."""
        if room_id not in self.room_members:
            self.room_members[room_id] = set()
        self.room_members[room_id].add(user_id)

        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)
        logger.info(f"🏠 User {user_id} joined room {room_id}")

    async def leave_room(self, room_id: int, user_id: int):
        """User leaves chat room."""
        if room_id in self.room_members:
            self.room_members[room_id].discard(user_id)
        if user_id in self.user_rooms:
            self.user_rooms[user_id].discard(room_id)
        logger.info(f"🚪 User {user_id} left room {room_id}")

    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user."""
        if user_id not in self.active_connections:
            return

        disconnected = set()
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                disconnected.add(websocket)

        # Remove disconnected sockets
        for ws in disconnected:
            self.active_connections[user_id].discard(ws)

    async def broadcast_to_room(
        self,
        room_id: int,
        message: dict,
        exclude_user_id: Optional[int] = None
    ):
        """Send message to all room members."""
        if room_id not in self.room_members:
            return

        for user_id in self.room_members[room_id]:
            if user_id == exclude_user_id:
                continue
            await self.send_personal_message(message, user_id)

    async def broadcast_to_users(self, message: dict, user_ids: List[int]):
        """Send message to multiple users."""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)

    async def send_notification(self, user_id: int, notification: dict):
        """Send real-time notification."""
        await self.send_personal_message({
            "type": "notification",
            **notification
        }, user_id)

    def get_online_users(self) -> List[int]:
        """Get list of online users."""
        return list(self.active_connections.keys())

    def is_user_online(self, user_id: int) -> bool:
        """Check if user is online."""
        return user_id in self.active_connections

    def get_room_online_members(self, room_id: int) -> List[int]:
        """Get online room members."""
        if room_id not in self.room_members:
            return []
        return [
            uid for uid in self.room_members[room_id]
            if uid in self.active_connections
        ]


# Singleton instance
manager = ConnectionManager()
