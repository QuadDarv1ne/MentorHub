"""
Message Routes
Placeholder for message/chat-related routes
TODO: Implement message routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_messages():
    """Get list of messages"""
    return {"message": "Messages endpoint - coming soon"}

