"""
Payment Routes
Placeholder for payment-related routes
TODO: Implement payment routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_payments():
    """Get list of payments"""
    return {"message": "Payments endpoint - coming soon"}

