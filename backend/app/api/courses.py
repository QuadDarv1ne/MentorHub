"""
Course Routes
Placeholder for course-related routes
TODO: Implement course routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_courses():
    """Get list of courses"""
    return {"message": "Courses endpoint - coming soon"}

