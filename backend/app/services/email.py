"""
Email service for sending notifications
"""
import logging
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST if hasattr(settings, 'SMTP_HOST') else None
        self.smtp_port = settings.SMTP_PORT if hasattr(settings, 'SMTP_PORT') else 587
        self.smtp_user = settings.SMTP_USER if hasattr(settings, 'SMTP_USER') else None
        self.smtp_password = settings.SMTP_PASSWORD if hasattr(settings, 'SMTP_PASSWORD') else None
        self.from_email = settings.FROM_EMAIL if hasattr(settings, 'FROM_EMAIL') else 'noreply@mentorhub.com'
        self.enabled = all([self.smtp_host, self.smtp_user, self.smtp_password])
        
        if not self.enabled:
            logger.warning("Email service is disabled - SMTP credentials not configured")
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        html: bool = False
    ) -> bool:
        """Send an email"""
        if not self.enabled:
            logger.info(f"[EMAIL DISABLED] Would send to {to_email}: {subject}")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            if html:
                part = MIMEText(body, 'html')
            else:
                part = MIMEText(body, 'plain')
            
            msg.attach(part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_welcome_email(self, email: str, name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Добро пожаловать в MentorHub!"
        body = f"""
        Привет, {name}!
        
        Добро пожаловать на платформу MentorHub.
        
        Теперь вы можете:
        - Находить опытных менторов
        - Бронировать сессии
        - Проходить курсы
        - Отслеживать свой прогресс
        
        Начните с поиска ментора в вашей области!
        
        С уважением,
        Команда MentorHub
        """
        
        return self.send_email(email, subject, body)
    
    def send_session_confirmation(
        self, 
        email: str, 
        session_topic: str, 
        scheduled_time: str
    ) -> bool:
        """Send session confirmation email"""
        subject = "Подтверждение бронирования сессии"
        body = f"""
        Ваша сессия успешно забронирована!
        
        Тема: {session_topic}
        Время: {scheduled_time}
        
        Ссылка на встречу будет отправлена за 15 минут до начала.
        
        С уважением,
        Команда MentorHub
        """
        
        return self.send_email(email, subject, body)
    
    def send_session_reminder(
        self,
        email: str,
        session_topic: str,
        meeting_link: str,
        time_until: str
    ) -> bool:
        """Send session reminder"""
        subject = f"Напоминание о сессии через {time_until}"
        body = f"""
        Напоминаем о предстоящей сессии:
        
        Тема: {session_topic}
        Начало через: {time_until}
        
        Ссылка на встречу: {meeting_link}
        
        До встречи!
        Команда MentorHub
        """
        
        return self.send_email(email, subject, body)


# Singleton instance
email_service = EmailService()
