"""
Mentor Routes
Placeholder for mentor-related routes
TODO: Implement mentor routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_mentors():
    """Get list of mentors"""
    return {"message": "Mentors endpoint - coming soon"}

