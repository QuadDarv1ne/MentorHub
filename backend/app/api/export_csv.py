"""
CSV Export for User Data

Converts user data to CSV format.
"""

import csv
import io
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import StreamingResponse


def export_as_csv(data: Dict[str, Any]) -> StreamingResponse:
    """
    Export user data to CSV format.
    
    Args:
        data: User data dictionary from collect_user_data()
    
    Returns:
        StreamingResponse with CSV file
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Export user profile information
    writer.writerow(["Field", "Value"])
    writer.writerow(["Username", data["user"]["username"]])
    writer.writerow(["Email", data["user"]["email"]])
    writer.writerow(["Full Name", data["user"]["full_name"]])
    writer.writerow(["Role", data["user"]["role"]])
    writer.writerow(["Export Date", data["export_date"]])
    writer.writerow([])
    
    # Sessions
    writer.writerow(["Sessions"])
    writer.writerow(["ID", "Student ID", "Mentor ID", "Scheduled At", "Duration", "Status"])
    for session in data["sessions"]:
        writer.writerow([
            session["id"],
            session["student_id"],
            session["mentor_id"],
            session["scheduled_at"],
            session["duration_minutes"],
            session["status"]
        ])
    writer.writerow([])
    
    # Payments
    writer.writerow(["Payments"])
    writer.writerow(["ID", "Student ID", "Mentor ID", "Amount", "Currency", "Status", "Created At"])
    for payment in data["payments"]:
        writer.writerow([
            payment["id"],
            payment["student_id"],
            payment["mentor_id"],
            payment["amount"],
            payment["currency"],
            payment["status"],
            payment["created_at"]
        ])
    
    output.seek(0)
    
    filename = f"mentorhub_data_export_{data['user']['username']}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
