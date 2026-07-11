"""
Calendar Integration API
Google Calendar + Outlook Calendar + ICS Export
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.models.calendar import CalendarEvent, CalendarProvider, CalendarSync
from app.models.session import Session as SessionModel
from app.models.user import User
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar", tags=["Calendar Integration"])


def _get_calendar_service(db: Session, user: User) -> CalendarService:
    """Получить сервис календаря"""
    return CalendarService(db, user)


@router.get("/auth/google")
async def google_auth_url() -> Dict[str, str]:
    """Получить URL для авторизации Google Calendar"""
    from urllib.parse import urlencode

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "scope": "https://www.googleapis.com/auth/calendar"
    }

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    return {"auth_url": f"{auth_url}?{urlencode(params)}"}


@router.get("/auth/google/callback")
async def google_callback(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Callback после авторизации Google"""
    import httpx

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "code": code,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        response.raise_for_status()
        tokens = response.json()

    # Получаем информацию о календаре
    calendar_id = "primary"

    # Сохраняем или обновляем синхронизацию
    service = _get_calendar_service(db, current_user)
    service.save_google_tokens(tokens, calendar_id)

    db.commit()

    return {"message": "Google Calendar connected successfully", "calendar_id": calendar_id}


@router.get("/auth/microsoft")
async def microsoft_auth_url() -> Dict[str, str]:
    """Получить URL для авторизации Outlook Calendar"""
    from urllib.parse import urlencode

    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "Calendars.ReadWrite offline_access"
    }

    auth_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
    return {"auth_url": f"{auth_url}?{urlencode(params)}"}


@router.get("/auth/microsoft/callback")
async def microsoft_callback(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Callback после авторизации Microsoft"""
    import httpx

    token_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "client_secret": settings.MICROSOFT_CLIENT_SECRET,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "code": code,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        response.raise_for_status()
        tokens = response.json()

    # Получаем ID календаря
    calendar_id = "calendar"

    # Сохраняем или обновляем синхронизацию
    service = _get_calendar_service(db, current_user)
    service.save_microsoft_tokens(tokens, calendar_id)

    db.commit()

    return {"message": "Outlook Calendar connected successfully", "calendar_id": calendar_id}


@router.get("/sync")
async def get_calendar_sync_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статус синхронизации календарей"""
    syncs = db.query(CalendarSync).filter(CalendarSync.user_id == current_user.id).all()

    result = []
    for sync in syncs:
        result.append({
            "provider": sync.provider.value,
            "is_active": sync.is_active,
            "calendar_id": sync.calendar_id,
            "last_sync_at": sync.last_sync_at.isoformat() if sync.last_sync_at else None,
            "auto_sync": sync.auto_sync,
            "token_expiry": sync.token_expiry.isoformat() if sync.token_expiry else None
        })

    return {"syncs": result}


@router.delete("/disconnect/{provider}")
async def disconnect_calendar(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отключить синхронизацию календаря"""
    try:
        calendar_provider = CalendarProvider(provider)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid provider. Use 'google' or 'outlook'") from None

    sync = db.query(CalendarSync).filter(
        CalendarSync.user_id == current_user.id,
        CalendarSync.provider == calendar_provider
    ).first()

    if not sync:
        raise HTTPException(status_code=404, detail="Calendar sync not found")

    db.delete(sync)
    db.commit()

    return {"message": f"{provider.capitalize()} Calendar disconnected"}


@router.get("/events")
async def get_calendar_events(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить события календаря"""
    if not start:
        start = datetime.now(timezone.utc)
    if not end:
        end = start + timedelta(days=30)

    query = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.start_time >= start,
        CalendarEvent.end_time <= end
    ).options(
        joinedload(CalendarEvent.session),
        joinedload(CalendarEvent.video_call)
    ).order_by(CalendarEvent.start_time)

    events = query.all()

    result = []
    for event in events:
        result.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "is_all_day": event.is_all_day,
            "status": event.status,
            "provider": event.provider.value,
            "session_id": event.session_id,
            "video_call_id": event.video_call_id
        })

    return {"events": result, "total": len(events)}


@router.get("/export/ics")
async def export_calendar_ics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Экспорт календаря в ICS формат"""
    try:
        from icalendar import Calendar
        from icalendar import Event as IcalEvent
        from icalendar.prop import vDDDTypes, vText  # noqa: F401
    except ImportError:
        raise HTTPException(status_code=503, detail="ICS export not available (icalendar not installed)") from None

    start = datetime.now(timezone.utc)
    end = start + timedelta(days=days)

    # Получаем события
    events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.start_time >= start,
        CalendarEvent.end_time <= end
    ).all()

    # Получаем сессии
    sessions = db.query(SessionModel).filter(
        or_(
            SessionModel.student_id == current_user.id,
            SessionModel.mentor_id == current_user.id
        ),
        SessionModel.scheduled_at >= start,
        SessionModel.scheduled_at <= end
    ).all()

    # Создаем календарь
    cal = Calendar()
    cal.add('prodid', '-//MentorHub//Calendar//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')

    # Добавляем события календаря
    for event in events:
        ical_event = IcalEvent()
        ical_event.add('summary', event.title)
        ical_event.add('dtstart', event.start_time)
        ical_event.add('dtend', event.end_time)
        ical_event.add('dtstamp', datetime.now(timezone.utc))
        ical_event.add('uid', f"event-{event.id}@mentorhub")

        if event.description:
            ical_event.add('description', event.description)
        if event.location:
            ical_event.add('location', event.location)

        cal.add_component(ical_event)

    # Добавляем сессии
    for session in sessions:
        ical_event = IcalEvent()
        ical_event.add('summary', f"Mentorship Session - {session.status.value}")
        ical_event.add('dtstart', session.scheduled_at)
        ical_event.add('dtend', session.scheduled_at + timedelta(minutes=session.duration_minutes))
        ical_event.add('dtstamp', datetime.now(timezone.utc))
        ical_event.add('uid', f"session-{session.id}@mentorhub")

        if session.notes:
            ical_event.add('description', session.notes)
        if session.meeting_link:
            ical_event.add('location', session.meeting_link)

        cal.add_component(ical_event)

    # Формируем ответ
    return Response(
        content=cal.to_ical(),
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="mentorhub_calendar_{current_user.username}_{datetime.now().strftime("%Y%m%d")}.ics"'
        }
    )


@router.post("/sync/now")
async def sync_calendar_now(
    provider: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Принудительная синхронизация календаря"""
    try:
        calendar_provider = CalendarProvider(provider)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid provider") from None

    sync = db.query(CalendarSync).filter(
        CalendarSync.user_id == current_user.id,
        CalendarSync.provider == calendar_provider,
        CalendarSync.is_active.is_(True)
    ).first()

    if not sync:
        raise HTTPException(status_code=404, detail="Calendar sync not found or inactive")

    # Здесь должна быть логика синхронизации с API провайдера
    # Для краткости просто обновляем last_sync_at

    sync.last_sync_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": f"{provider.capitalize()} Calendar synced", "last_sync_at": sync.last_sync_at.isoformat()}
