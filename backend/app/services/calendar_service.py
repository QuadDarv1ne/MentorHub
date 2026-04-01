"""
Calendar Service
Бизнес-логика для календаря и OAuth интеграций
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from app.models.user import User
from app.models.calendar import CalendarSync, CalendarEvent, CalendarProvider
from app.models.session import Session as SessionModel
from app.models.video_call import VideoCall


class GoogleCalendarService:
    """Сервис для работы с Google Calendar"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_auth_url(self) -> str:
        """Получить URL для авторизации"""
        from urllib.parse import urlencode

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "scope": "https://www.googleapis.com/auth/calendar"
        }

        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """Обменять код на токены"""
        import httpx

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "grant_type": "authorization_code"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()


class MicrosoftCalendarService:
    """Сервис для работы с Outlook Calendar"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.tenant_id = tenant_id

    def get_auth_url(self) -> str:
        """Получить URL для авторизации"""
        from urllib.parse import urlencode

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "Calendars.ReadWrite offline_access",
        }

        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize?{urlencode(params)}"

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """Обменять код на токены"""
        import httpx

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "grant_type": "authorization_code"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()


class CalendarService:
    """Основной сервис для управления календарём"""

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def get_sync_status(self, provider: CalendarProvider) -> Optional[CalendarSync]:
        """Получить статус синхронизации"""
        return self.db.query(CalendarSync).filter(
            CalendarSync.user_id == self.user.id,
            CalendarSync.provider == provider
        ).first()

    def save_google_tokens(self, tokens: Dict[str, Any], calendar_id: str = "primary"):
        """Сохранить токены Google"""
        existing = self.get_sync_status(CalendarProvider.GOOGLE)

        if existing:
            existing.access_token = tokens["access_token"]
            existing.refresh_token = tokens.get("refresh_token", existing.refresh_token)
            existing.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=tokens.get("expires_in", 3600))
            existing.calendar_id = calendar_id
            existing.is_active = True
        else:
            sync = CalendarSync(
                user_id=self.user.id,
                provider=CalendarProvider.GOOGLE,
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                token_expiry=datetime.now(timezone.utc) + timedelta(seconds=tokens.get("expires_in", 3600)),
                calendar_id=calendar_id,
                is_active=True
            )
            self.db.add(sync)

        self.db.commit()

    def save_microsoft_tokens(self, tokens: Dict[str, Any], calendar_id: str = "primary"):
        """Сохранить токены Microsoft"""
        existing = self.get_sync_status(CalendarProvider.OUTLOOK)

        if existing:
            existing.access_token = tokens["access_token"]
            existing.refresh_token = tokens.get("refresh_token", existing.refresh_token)
            existing.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=tokens.get("expires_in", 3600))
            existing.calendar_id = calendar_id
            existing.is_active = True
        else:
            sync = CalendarSync(
                user_id=self.user.id,
                provider=CalendarProvider.OUTLOOK,
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                token_expiry=datetime.now(timezone.utc) + timedelta(seconds=tokens.get("expires_in", 3600)),
                calendar_id=calendar_id,
                is_active=True
            )
            self.db.add(sync)

        self.db.commit()

    def disconnect_calendar(self, provider: CalendarProvider) -> bool:
        """Отключить синхронизацию календаря"""
        sync = self.get_sync_status(provider)
        if not sync:
            return False

        sync.is_active = False
        sync.access_token = None
        sync.refresh_token = None
        self.db.commit()
        return True

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        """Получить события пользователя"""
        query = self.db.query(CalendarEvent).filter(
            CalendarEvent.user_id == self.user.id
        )

        if start_date:
            query = query.filter(CalendarEvent.start_time >= start_date)
        if end_date:
            query = query.filter(CalendarEvent.end_time <= end_date)

        return query.order_by(CalendarEvent.start_time).all()

    def sync_sessions_to_calendar(self) -> int:
        """Синхронизировать сессии с календарём"""
        sessions = self.db.query(SessionModel).filter(
            or_(
                SessionModel.student_id == self.user.id,
                SessionModel.mentor_id == self.user.id
            )
        ).all()

        synced = 0
        for session in sessions:
            event = self.db.query(CalendarEvent).filter(
                CalendarEvent.external_id == f"session_{session.id}"
            ).first()

            if not event:
                event = CalendarEvent(
                    user_id=self.user.id,
                    title=f"Session: {session.title}",
                    description=session.description,
                    start_time=session.scheduled_at,
                    end_time=session.scheduled_at + timedelta(hours=session.duration_hours or 1),
                    external_id=f"session_{session.id}",
                    source="session"
                )
                self.db.add(event)
                synced += 1

        self.db.commit()
        return synced

    def sync_video_calls_to_calendar(self) -> int:
        """Синхронизировать видеозвонки с календарём"""
        calls = self.db.query(VideoCall).filter(
            or_(
                VideoCall.creator_id == self.user.id,
                VideoCall.participant_id == self.user.id
            ),
            VideoCall.scheduled_at != None
        ).all()

        synced = 0
        for call in calls:
            event = self.db.query(CalendarEvent).filter(
                CalendarEvent.external_id == f"call_{call.id}"
            ).first()

            if not event:
                event = CalendarEvent(
                    user_id=self.user.id,
                    title=f"Video Call: {call.title or 'Call'}",
                    description=call.description,
                    start_time=call.scheduled_at,
                    end_time=call.scheduled_at + timedelta(hours=1),
                    external_id=f"call_{call.id}",
                    source="video_call"
                )
                self.db.add(event)
                synced += 1

        self.db.commit()
        return synced


# Фабрика сервисов
def create_google_service() -> GoogleCalendarService:
    """Создать Google Calendar сервис"""
    return GoogleCalendarService(
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "")
    )


def create_microsoft_service() -> MicrosoftCalendarService:
    """Создать Microsoft Calendar сервис"""
    return MicrosoftCalendarService(
        client_id=os.getenv("MICROSOFT_CLIENT_ID", ""),
        client_secret=os.getenv("MICROSOFT_CLIENT_SECRET", ""),
        redirect_uri=os.getenv("MICROSOFT_REDIRECT_URI", ""),
        tenant_id=os.getenv("MICROSOFT_TENANT_ID", "common")
    )
