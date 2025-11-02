"""
Session Routes
Placeholder for session-related routes
TODO: Implement session routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_sessions():
    """Get list of sessions"""
    return {"message": "Sessions endpoint - coming soon"}

