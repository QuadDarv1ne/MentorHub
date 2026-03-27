"""
User Data Export API Router

GDPR compliance data export endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.utils.cache import cached
from app.api.export_data import collect_user_data, get_user_data_counts
from app.api.export_csv import export_as_csv
from app.api.export_pdf import export_as_pdf
from app.api.export_excel import export_as_excel

router = APIRouter(prefix="/export", tags=["Data Export"])


@router.get("/data", summary="Export all user data")
async def export_user_data(
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export all user data in JSON, CSV, PDF, or Excel format.
    
    Includes:
    - User profile
    - Session history
    - Payment history
    - Reviews
    - Learning progress
    - Achievements
    - Messages
    - Course enrollments
    
    GDPR compliance: users can request a copy of their data.
    """
    # Collect all user data
    user_data = collect_user_data(db, current_user)
    
    # Return in requested format
    format_lower = format.lower()
    
    if format_lower == "csv":
        return export_as_csv(user_data)
    elif format_lower == "pdf":
        return export_as_pdf(user_data)
    elif format_lower in ["excel", "xlsx"]:
        return export_as_excel(user_data)
    else:
        # Default to JSON
        return JSONResponse(
            content=user_data,
            headers={
                "Content-Disposition": f'attachment; filename="mentorhub_data_export_{current_user.id}_{user_data["export_date"][:10]}.json"'
            }
        )


@router.get("/data/summary", summary="Get user data summary statistics")
@cached(ttl=300)  # Cache for 5 minutes
async def get_data_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get summary statistics of user data without details.
    """
    counts = get_user_data_counts(db, current_user.id)
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "data_summary": counts,
        "total_records": sum(counts.values())
    }
