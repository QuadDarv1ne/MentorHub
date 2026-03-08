#!/usr/bin/env python3
"""
Generate PDF report for MentorHub Graceful Shutdown fixes
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Register fonts
pdfmetrics.registerFont(TTFont('Times New Roman', '/usr/share/fonts/truetype/english/Times-New-Roman.ttf'))
pdfmetrics.registerFont(TTFont('SimHei', '/usr/share/fonts/truetype/chinese/SimHei.ttf'))
registerFontFamily('Times New Roman', normal='Times New Roman', bold='Times New Roman')
registerFontFamily('SimHei', normal='SimHei', bold='SimHei')

# Create document
doc = SimpleDocTemplate(
    "/home/z/my-project/download/mentorhub_fixes/MentorHub_Graceful_Shutdown_Guide.pdf",
    pagesize=A4,
    title="MentorHub Graceful Shutdown Guide",
    author="Z.ai",
    creator="Z.ai",
    subject="Technical guide for fixing graceful shutdown issues in MentorHub"
)

# Styles
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Title'],
    fontName='Times New Roman',
    fontSize=24,
    spaceAfter=30,
    alignment=TA_CENTER
)

h1_style = ParagraphStyle(
    'H1Style',
    parent=styles['Heading1'],
    fontName='Times New Roman',
    fontSize=16,
    spaceBefore=20,
    spaceAfter=12,
    textColor=colors.HexColor('#1F4E79')
)

h2_style = ParagraphStyle(
    'H2Style',
    parent=styles['Heading2'],
    fontName='Times New Roman',
    fontSize=14,
    spaceBefore=15,
    spaceAfter=8,
    textColor=colors.HexColor('#2E75B6')
)

body_style = ParagraphStyle(
    'BodyStyle',
    parent=styles['Normal'],
    fontName='Times New Roman',
    fontSize=10.5,
    leading=16,
    alignment=TA_JUSTIFY,
    spaceAfter=8
)

code_style = ParagraphStyle(
    'CodeStyle',
    fontName='Courier',
    fontSize=8,
    leading=11,
    backColor=colors.HexColor('#F5F5F5'),
    leftIndent=10,
    rightIndent=10,
    spaceBefore=8,
    spaceAfter=8
)

bullet_style = ParagraphStyle(
    'BulletStyle',
    parent=body_style,
    leftIndent=20,
    bulletIndent=10
)

# Content
story = []

# Title
story.append(Paragraph("<b>MentorHub: Graceful Shutdown Guide</b>", title_style))
story.append(Spacer(1, 20))
story.append(Paragraph("Technical documentation for fixing container termination issues", 
    ParagraphStyle('Subtitle', fontName='Times New Roman', fontSize=12, alignment=TA_CENTER)))
story.append(Spacer(1, 30))

# Problem Analysis
story.append(Paragraph("<b>1. Problem Analysis</b>", h1_style))

story.append(Paragraph(
    "The MentorHub container experiences improper shutdown behavior. Analysis of the logs shows "
    "that the backend process ignores the SIGTERM signal and continues running until Supervisord "
    "forcefully kills it with SIGKILL after approximately 10 seconds. This behavior is problematic "
    "for several important reasons that affect both user experience and data integrity.",
    body_style
))

story.append(Spacer(1, 10))
story.append(Paragraph("<b>Log Evidence:</b>", h2_style))

log_text = """2026-03-08 11:01:08,889 WARN received SIGTERM indicating exit request
2026-03-08 11:01:08,890 INFO waiting for backend, frontend to die
...
2026-03-08 11:01:19,704 WARN killing 'backend' (26) with SIGKILL
2026-03-08 11:01:20,705 WARN stopped: backend (terminated by SIGKILL)"""
story.append(Preformatted(log_text, code_style))

story.append(Spacer(1, 10))
story.append(Paragraph("<b>Impact of Current Behavior:</b>", h2_style))

impacts = [
    "Active user connections are abruptly terminated, resulting in HTTP 502/504 errors",
    "In-flight requests may lose data that has not been written to the database",
    "Database connections may remain open, causing connection pool exhaustion",
    "Container restart takes longer (waiting for the SIGKILL timeout)",
    "Redis cache connections may not be properly closed"
]

for impact in impacts:
    story.append(Paragraph(f"• {impact}", bullet_style))

story.append(Spacer(1, 15))

# Root Causes
story.append(Paragraph("<b>2. Root Causes Identified</b>", h1_style))

story.append(Paragraph("<b>2.1 Supervisor Configuration Issues</b>", h2_style))
story.append(Paragraph(
    "The Dockerfile creates the Supervisor configuration dynamically using shell echo commands. "
    "This approach results in several critical omissions that prevent proper process termination. "
    "The configuration lacks essential directives for graceful shutdown, including stopasgroup, "
    "killasgroup, and adequate timeout settings. Additionally, logs are written to files instead "
    "of Docker stdout/stderr streams, making debugging more difficult.",
    body_style
))

story.append(Paragraph("<b>2.2 Missing Signal Handlers in FastAPI</b>", h2_style))
story.append(Paragraph(
    "The FastAPI application in backend/app/main.py does not register signal handlers for SIGTERM "
    "and SIGINT. While the lifespan context manager contains shutdown logic, this code only executes "
    "when the application shuts down cleanly through its internal mechanisms. When a SIGTERM signal "
    "arrives from Docker or Kubernetes, the application does not trap it, and the process continues "
    "running as if nothing happened.",
    body_style
))

story.append(Paragraph("<b>2.3 Uvicorn Configuration</b>", h2_style))
story.append(Paragraph(
    "The uvicorn startup command in the Supervisor configuration does not include the "
    "--timeout-graceful-shutdown flag. This flag tells uvicorn how long to wait for active "
    "connections to complete before forcing shutdown. Without it, uvicorn may not properly "
    "coordinate the shutdown sequence with the underlying FastAPI application.",
    body_style
))

story.append(PageBreak())

# Solutions
story.append(Paragraph("<b>3. Recommended Solutions</b>", h1_style))

story.append(Paragraph("<b>3.1 Create Dedicated Supervisor Configuration File</b>", h2_style))
story.append(Paragraph(
    "Replace the inline shell script configuration in the Dockerfile with a proper configuration "
    "file stored in the repository. This approach provides better maintainability, version control, "
    "and ensures all necessary settings are included.",
    body_style
))

story.append(Paragraph("<b>File: deploy/supervisor/app.conf</b>", body_style))

config_text = """[supervisord]
nodaemon=true
logfile=/dev/null
pidfile=/var/run/supervisord.pid
user=root

[program:backend]
command=uvicorn app.main:app --host 0.0.0.0 --port %(ENV_BACKEND_PORT)s \\
       --workers 2 --timeout-graceful-shutdown 30
directory=/app/backend
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stopwaitsecs=35
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0"""
story.append(Preformatted(config_text, code_style))

story.append(Spacer(1, 10))
story.append(Paragraph(
    "<b>Key Configuration Parameters Explained:</b>",
    body_style
))

params = [
    ("stopasgroup=true", "Ensures SIGTERM is sent to the entire process group, including child workers"),
    ("killasgroup=true", "Ensures SIGKILL is sent to the entire process group if stopwaitsecs expires"),
    ("stopwaitsecs=35", "Gives the application 35 seconds to complete shutdown before SIGKILL"),
    ("timeout-graceful-shutdown 30", "Uvicorn waits 30 seconds for active connections to complete"),
    ("stdout_logfile=/dev/stdout", "Routes logs to Docker stdout for visibility via docker logs")
]

# Table for parameters
table_data = [[Paragraph('<b>Parameter</b>', ParagraphStyle('TableHeader', fontName='Times New Roman', fontSize=10, textColor=colors.white)),
               Paragraph('<b>Purpose</b>', ParagraphStyle('TableHeader', fontName='Times New Roman', fontSize=10, textColor=colors.white))]]
for param, purpose in params:
    table_data.append([param, purpose])

param_table = Table(table_data, colWidths=[4*cm, 12*cm])
param_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 1), (-1, -1), 'Times New Roman'),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(param_table)
story.append(Spacer(1, 15))

story.append(Paragraph("<b>3.2 Add Signal Handlers to FastAPI Application</b>", h2_style))
story.append(Paragraph(
    "Modify backend/app/main.py to register signal handlers that coordinate graceful shutdown. "
    "These handlers work in conjunction with the lifespan context manager to ensure all resources "
    "are properly released when the application receives a termination signal.",
    body_style
))

signal_code = """import signal
import sys

_shutdown_event = asyncio.Event()
_shutdown_in_progress = False

def signal_handler(signum, frame):
    global _shutdown_in_progress
    signal_name = signal.Signals(signum).name
    if _shutdown_in_progress:
        logger.warning(f"Shutdown already in progress")
        return
    _shutdown_in_progress = True
    logger.info(f"Received {signal_name}. Initiating graceful shutdown...")
    _shutdown_event.set()

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)"""
story.append(Preformatted(signal_code, code_style))

story.append(PageBreak())

story.append(Paragraph("<b>3.3 Update Dockerfile</b>", h2_style))
story.append(Paragraph(
    "Modify the Dockerfile to copy the Supervisor configuration from the repository instead of "
    "generating it inline. This change provides better maintainability and ensures all necessary "
    "settings are consistently applied.",
    body_style
))

dockerfile_code = """# Replace lines 63-86 in Dockerfile with:

# Supervisor Configuration
WORKDIR /app
RUN mkdir -p /var/log/supervisor

# Copy prepared configuration file
COPY deploy/supervisor/app.conf /etc/supervisor/conf.d/app.conf

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh"""
story.append(Preformatted(dockerfile_code, code_style))

story.append(Spacer(1, 15))

story.append(Paragraph("<b>3.4 Update start.sh Script</b>", h2_style))
story.append(Paragraph(
    "The startup script must use the exec command to replace the shell process with supervisord. "
    "This ensures that signals reach supervisord directly rather than being trapped by the shell. "
    "The script should also handle the PORT environment variable for cloud platform compatibility.",
    body_style
))

startsh_code = """#!/bin/bash
set -e

# Get port from environment (for Render/Railway/Heroku)
BACKEND_PORT="${PORT:-${BACKEND_PORT:-8000}}"

echo "Starting MentorHub..."
echo "Backend port: $BACKEND_PORT"

# Update supervisor config with actual port
sed -i "s/%(ENV_BACKEND_PORT)s/$BACKEND_PORT/g" /etc/supervisor/conf.d/app.conf

# CRITICAL: exec replaces shell with supervisord
# This allows signals to reach supervisord directly
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf"""
story.append(Preformatted(startsh_code, code_style))

story.append(Spacer(1, 20))

# Expected Results
story.append(Paragraph("<b>4. Expected Results After Fixes</b>", h1_style))
story.append(Paragraph(
    "After implementing all the recommended changes, the container shutdown logs should show "
    "a clean termination sequence without any SIGKILL signals. The following represents the "
    "expected log output during a normal container restart or scale-down event.",
    body_style
))

expected_log = """2026-03-08 11:01:08,889 WARN received SIGTERM indicating exit request
2026-03-08 11:01:08,890 INFO waiting for backend, frontend to die
2026-03-08 11:01:09,100 INFO Received SIGTERM. Initiating graceful shutdown...
2026-03-08 11:01:09,150 INFO Closing database connections...
2026-03-08 11:01:09,200 INFO Closing Redis connections...
2026-03-08 11:01:09,250 INFO Graceful shutdown complete
2026-03-08 11:01:09,300 INFO stopped: backend (exit status 0)
2026-03-08 11:01:09,350 INFO stopped: frontend (exit status 0)"""
story.append(Preformatted(expected_log, code_style))

story.append(Spacer(1, 15))

story.append(Paragraph("<b>Benefits:</b>", h2_style))
benefits = [
    "Active requests complete successfully before shutdown",
    "Database connections are properly closed, preventing connection leaks",
    "Redis cache connections are cleanly terminated",
    "Container restarts complete in seconds instead of waiting for SIGKILL timeout",
    "Users experience no 502/504 errors during deployments"
]
for benefit in benefits:
    story.append(Paragraph(f"• {benefit}", bullet_style))

story.append(PageBreak())

# Platform Compatibility
story.append(Paragraph("<b>5. Cross-Platform Deployment Compatibility</b>", h1_style))
story.append(Paragraph(
    "The recommended changes maintain compatibility with all major cloud platforms. Each platform "
    "has specific requirements for container deployment, and the solution addresses these while "
    "keeping the configuration flexible and maintainable.",
    body_style
))

# Platform compatibility table
platform_data = [
    [Paragraph('<b>Platform</b>', ParagraphStyle('TH', fontName='Times New Roman', fontSize=10, textColor=colors.white)),
     Paragraph('<b>Port Handling</b>', ParagraphStyle('TH', fontName='Times New Roman', fontSize=10, textColor=colors.white)),
     Paragraph('<b>Notes</b>', ParagraphStyle('TH', fontName='Times New Roman', fontSize=10, textColor=colors.white))],
    ['Render', 'Uses $PORT variable', 'Automatically injects PORT'],
    ['Railway', 'Uses $PORT variable', 'Similar to Render'],
    ['Heroku', 'Uses $PORT variable', 'Dyno lifecycle events supported'],
    ['Fly.io', 'Uses $PORT variable', 'Health checks recommended'],
    ['Amvera', 'Standard port 8000', 'Russian cloud platform'],
    ['VPS/Docker', 'Uses configured ports', 'Full control over networking'],
    ['Kubernetes', 'Configurable via YAML', 'Readiness/liveness probes supported']
]

platform_table = Table(platform_data, colWidths=[3*cm, 4*cm, 9*cm])
platform_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 1), (-1, -1), 'Times New Roman'),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('BACKGROUND', (0, 1), (-1, 1), colors.white),
    ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F5F5F5')),
    ('BACKGROUND', (0, 3), (-1, 3), colors.white),
    ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F5F5F5')),
    ('BACKGROUND', (0, 5), (-1, 5), colors.white),
    ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#F5F5F5')),
    ('BACKGROUND', (0, 7), (-1, 7), colors.white),
]))
story.append(platform_table)
story.append(Spacer(1, 20))

# Summary
story.append(Paragraph("<b>6. Implementation Summary</b>", h1_style))
story.append(Paragraph(
    "The following files need to be created or modified to implement graceful shutdown in MentorHub. "
    "All changes are backward compatible and maintain the existing functionality while adding proper "
    "signal handling and shutdown coordination.",
    body_style
))

files_data = [
    [Paragraph('<b>File</b>', ParagraphStyle('TH', fontName='Times New Roman', fontSize=10, textColor=colors.white)),
     Paragraph('<b>Action</b>', ParagraphStyle('TH', fontName='Times New Roman', fontSize=10, textColor=colors.white)),
     Paragraph('<b>Changes</b>', ParagraphStyle('TH', fontName='Times New Roman', fontSize=10, textColor=colors.white))],
    ['deploy/supervisor/app.conf', 'Create', 'New supervisor configuration file'],
    ['backend/app/main.py', 'Modify', 'Add signal handlers + shutdown logic'],
    ['Dockerfile', 'Modify', 'Copy config file instead of inline echo'],
    ['start.sh', 'Modify', 'Add exec + PORT variable handling']
]

files_table = Table(files_data, colWidths=[5*cm, 2.5*cm, 8.5*cm])
files_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 1), (-1, -1), 'Times New Roman'),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(files_table)

# Build
doc.build(story)
print("PDF generated successfully!")
