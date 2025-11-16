"""
Notification service for various notification channels
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from app.services.email import email_service

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications through multiple channels"""
    
    def __init__(self):
        self.email_service = email_service
    
    async def send_notification(
        self,
        user_email: str,
        notification_type: str,
        data: Dict[str, Any],
        channels: list = None
    ) -> bool:
        """
        Send notification through specified channels
        
        Args:
            user_email: User's email address
            notification_type: Type of notification (welcome, session_confirmed, etc.)
            data: Notification data
            channels: List of channels to use (default: ['email'])
        
        Returns:
            bool: True if notification was sent successfully
        """
        if channels is None:
            channels = ['email']
        
        success = False
        
        if 'email' in channels:
            success = await self._send_email_notification(
                user_email,
                notification_type,
                data
            )
        
        # Future: Add more channels (SMS, Push, In-App)
        
        return success
    
    async def _send_email_notification(
        self,
        email: str,
        notification_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Send email notification based on type"""
        
        handlers = {
            'welcome': self._handle_welcome,
            'session_confirmed': self._handle_session_confirmed,
            'session_reminder': self._handle_session_reminder,
            'session_cancelled': self._handle_session_cancelled,
            'new_message': self._handle_new_message,
            'payment_received': self._handle_payment_received,
        }
        
        handler = handlers.get(notification_type)
        if not handler:
            logger.warning(f"Unknown notification type: {notification_type}")
            return False
        
        return handler(email, data)
    
    def _handle_welcome(self, email: str, data: Dict[str, Any]) -> bool:
        """Handle welcome notification"""
        return self.email_service.send_welcome_email(
            email,
            data.get('name', 'User')
        )
    
    def _handle_session_confirmed(self, email: str, data: Dict[str, Any]) -> bool:
        """Handle session confirmation notification"""
        return self.email_service.send_session_confirmation(
            email,
            data.get('topic', 'Mentoring Session'),
            data.get('scheduled_time', '')
        )
    
    def _handle_session_reminder(self, email: str, data: Dict[str, Any]) -> bool:
        """Handle session reminder notification"""
        return self.email_service.send_session_reminder(
            email,
            data.get('topic', 'Mentoring Session'),
            data.get('meeting_link', ''),
            data.get('time_until', '15 minutes')
        )
    
    def _handle_session_cancelled(self, email: str, data: Dict[str, Any]) -> bool:
        """Handle session cancellation notification"""
        subject = "Сессия отменена"
        body = f"""
        Сессия была отменена.
        
        Тема: {data.get('topic', 'N/A')}
        Время: {data.get('scheduled_time', 'N/A')}
        
        Вы можете забронировать новую сессию на платформе.
        
        С уважением,
        Команда MentorHub
        """
        
        return self.email_service.send_email(email, subject, body)
    
    def _handle_new_message(self, email: str, data: Dict[str, Any]) -> bool:
        """Handle new message notification"""
        subject = "Новое сообщение"
        body = f"""
        Вы получили новое сообщение от {data.get('sender_name', 'пользователя')}.
        
        Войдите на платформу, чтобы прочитать и ответить.
        
        С уважением,
        Команда MentorHub
        """
        
        return self.email_service.send_email(email, subject, body)
    
    def _handle_payment_received(self, email: str, data: Dict[str, Any]) -> bool:
        """Handle payment received notification"""
        subject = "Платёж получен"
        body = f"""
        Ваш платёж успешно обработан.
        
        Сумма: {data.get('amount', '0')} {data.get('currency', 'USD')}
        Сессия: {data.get('session_topic', 'N/A')}
        
        Квитанция доступна в вашем профиле.
        
        С уважением,
        Команда MentorHub
        """
        
        return self.email_service.send_email(email, subject, body)


# Singleton instance
notification_service = NotificationService()
