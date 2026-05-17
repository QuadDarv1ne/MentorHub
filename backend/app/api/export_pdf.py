"""
PDF Export for User Data

Converts user data to PDF format using ReportLab.
"""

import io
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import HTTPException, Response


def export_as_pdf(data: Dict[str, Any]) -> Response:
    """
    Export user data to PDF format.
    
    Args:
        data: User data dictionary from collect_user_data()
    
    Returns:
        Response with PDF file
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        raise HTTPException(status_code=503, detail="PDF export not available (reportlab not installed)")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    story = []
    
    # Title
    story.append(Paragraph("MentorHub Data Export", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # User information table
    user_info = [
        ["Username", data["user"]["username"]],
        ["Email", data["user"]["email"]],
        ["Full Name", data["user"]["full_name"] or "N/A"],
        ["Role", data["user"]["role"]],
        ["Export Date", data["export_date"]]
    ]
    
    user_table = Table(user_info, colWidths=[2*inch, 4*inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f7ff')])
    ]))
    story.append(user_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Statistics table
    stats_data = [
        ["Category", "Count"],
        ["Sessions", len(data["sessions"])],
        ["Payments", len(data["payments"])],
        ["Reviews", len(data["reviews"])],
        ["Progress Records", len(data["progress"])],
        ["Achievements", len(data["achievements"])],
        ["Messages", len(data["messages"])],
        ["Course Enrollments", len(data["enrollments"])]
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f7ff')])
    ]))
    story.append(stats_table)
    
    doc.build(story)
    buffer.seek(0)
    
    filename = f"mentorhub_export_{data['user']['username']}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
