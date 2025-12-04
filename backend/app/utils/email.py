"""
Email utility для отправки писем
Поддержка verification, password reset, notifications
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email уведомлений"""

    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USER', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'SMTP_FROM_EMAIL', 'noreply@mentorhub.com')
        self.from_name = getattr(settings, 'SMTP_FROM_NAME', 'MentorHub')

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Отправка email
        
        Args:
            to_email: Email получателя
            subject: Тема письма
            html_content: HTML содержимое
            text_content: Текстовая версия (опционально)
            
        Returns:
            True если успешно, False если ошибка
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email send")
            return False

        try:
            # Создаем сообщение
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Добавляем текстовую версию
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            # Добавляем HTML версию
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            # Отправляем
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"✅ Email sent to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False

    def send_verification_email(self, to_email: str, username: str, token: str) -> bool:
        """Отправка письма с подтверждением email"""
        verification_link = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .button {{ 
                    display: inline-block;
                    padding: 12px 30px;
                    background: #4F46E5;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 MentorHub</h1>
                </div>
                <div class="content">
                    <h2>Добро пожаловать, {username}!</h2>
                    <p>Спасибо за регистрацию на MentorHub. Пожалуйста, подтвердите ваш email адрес, нажав на кнопку ниже:</p>
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">Подтвердить Email</a>
                    </div>
                    <p>Или скопируйте эту ссылку в браузер:</p>
                    <p style="word-break: break-all; color: #6b7280;">{verification_link}</p>
                    <p>Эта ссылка действительна в течение 24 часов.</p>
                </div>
                <div class="footer">
                    <p>Если вы не регистрировались на MentorHub, просто проигнорируйте это письмо.</p>
                    <p>&copy; 2025 MentorHub. Все права защищены.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Добро пожаловать, {username}!
        
        Спасибо за регистрацию на MentorHub.
        Пожалуйста, подтвердите ваш email адрес, перейдя по ссылке:
        
        {verification_link}
        
        Эта ссылка действительна в течение 24 часов.
        
        Если вы не регистрировались на MentorHub, просто проигнорируйте это письмо.
        """
        
        return self.send_email(
            to_email=to_email,
            subject="Подтверждение email - MentorHub",
            html_content=html_content,
            text_content=text_content
        )

    def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """Отправка письма для сброса пароля"""
        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #DC2626; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .button {{ 
                    display: inline-block;
                    padding: 12px 30px;
                    background: #DC2626;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Сброс пароля</h1>
                </div>
                <div class="content">
                    <h2>Привет, {username}!</h2>
                    <p>Вы запросили сброс пароля для вашего аккаунта MentorHub.</p>
                    <p>Нажмите на кнопку ниже, чтобы создать новый пароль:</p>
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Сбросить пароль</a>
                    </div>
                    <p>Или скопируйте эту ссылку в браузер:</p>
                    <p style="word-break: break-all; color: #6b7280;">{reset_link}</p>
                    <p>Эта ссылка действительна в течение 1 часа.</p>
                    <p><strong>Если вы не запрашивали сброс пароля, немедленно проигнорируйте это письмо и свяжитесь с поддержкой.</strong></p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 MentorHub. Все права защищены.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Привет, {username}!
        
        Вы запросили сброс пароля для вашего аккаунта MentorHub.
        
        Перейдите по ссылке для создания нового пароля:
        {reset_link}
        
        Эта ссылка действительна в течение 1 часа.
        
        Если вы не запрашивали сброс пароля, немедленно проигнорируйте это письмо.
        """
        
        return self.send_email(
            to_email=to_email,
            subject="Сброс пароля - MentorHub",
            html_content=html_content,
            text_content=text_content
        )

    def send_session_notification(
        self, 
        to_email: str, 
        username: str, 
        session_date: str,
        mentor_name: str,
        session_link: str
    ) -> bool:
        """Уведомление о предстоящей сессии"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10B981; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .info-box {{ 
                    background: white;
                    border-left: 4px solid #10B981;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .button {{ 
                    display: inline-block;
                    padding: 12px 30px;
                    background: #10B981;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📅 Напоминание о сессии</h1>
                </div>
                <div class="content">
                    <h2>Привет, {username}!</h2>
                    <p>Напоминаем о вашей предстоящей менторской сессии:</p>
                    <div class="info-box">
                        <p><strong>Ментор:</strong> {mentor_name}</p>
                        <p><strong>Дата и время:</strong> {session_date}</p>
                    </div>
                    <div style="text-align: center;">
                        <a href="{session_link}" class="button">Присоединиться к сессии</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=to_email,
            subject=f"Напоминание: сессия с {mentor_name}",
            html_content=html_content
        )


# Singleton instance
email_service = EmailService()
