"""
Email сервис для отправки писем
"""

import html as html_lib
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email уведомлений"""

    # Timeout для SMTP подключений (секунды)
    SMTP_TIMEOUT = 30

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
        text_content: str | None = None
    ) -> bool:
        """Отправка email"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email send")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.SMTP_TIMEOUT) as server:
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
        safe_username = html_lib.escape(username)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #4F46E5; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>MentorHub</h1></div>
                <div class="content">
                    <h2>Добро пожаловать, {safe_username}!</h2>
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
        """

        return self.send_email(to_email=to_email, subject="Подтверждение email - MentorHub", html_content=html_content, text_content=text_content)

    def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """Отправка письма для сброса пароля"""
        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        safe_username = html_lib.escape(username)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #DC2626; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #DC2626; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>Сброс пароля</h1></div>
                <div class="content">
                    <h2>Привет, {safe_username}!</h2>
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
                <div class="footer"><p>&copy; 2025 MentorHub. Все права защищены.</p></div>
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
        """

        return self.send_email(to_email=to_email, subject="Сброс пароля - MentorHub", html_content=html_content, text_content=text_content)

    def send_session_notification(
        self,
        to_email: str,
        username: str,
        session_date: str,
        mentor_name: str,
        session_link: str
    ) -> bool:
        """Уведомление о предстоящей сессии"""
        safe_username = html_lib.escape(username)
        safe_mentor_name = html_lib.escape(mentor_name)
        safe_session_date = html_lib.escape(session_date)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10B981; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .info-box {{ background: white; border-left: 4px solid #10B981; padding: 15px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #10B981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>Напоминание о сессии</h1></div>
                <div class="content">
                    <h2>Привет, {safe_username}!</h2>
                    <p>Напоминаем о вашей предстоящей менторской сессии:</p>
                    <div class="info-box">
                        <p><strong>Ментор:</strong> {safe_mentor_name}</p>
                        <p><strong>Дата и время:</strong> {safe_session_date}</p>
                    </div>
                    <div style="text-align: center;">
                        <a href="{session_link}" class="button">Присоединиться к сессии</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return self.send_email(to_email=to_email, subject=f"Напоминание: сессия с {safe_mentor_name}", html_content=html_content)

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Приветственное письмо после регистрации"""
        safe_username = html_lib.escape(username)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10B981; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #10B981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>Добро пожаловать в MentorHub!</h1></div>
                <div class="content">
                    <h2>Привет, {safe_username}!</h2>
                    <p>Спасибо за регистрацию на платформе MentorHub.</p>
                    <p>Теперь вы можете:</p>
                    <ul>
                        <li>Найти опытного ментора для обучения</li>
                        <li>Записаться на индивидуальную сессию</li>
                        <li>Пройти курсы и получить сертификаты</li>
                    </ul>
                    <div style="text-align: center;">
                        <a href="{settings.FRONTEND_URL}/mentors" class="button">Найти ментора</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return self.send_email(to_email=to_email, subject="Добро пожаловать в MentorHub!", html_content=html_content)

    def send_session_reminder(
        self,
        to_email: str,
        username: str,
        mentor_name: str,
        session_date: str,
        session_link: str
    ) -> bool:
        """Напоминание о сессии за 24 часа"""
        safe_username = html_lib.escape(username)
        safe_mentor_name = html_lib.escape(mentor_name)
        safe_session_date = html_lib.escape(session_date)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #F59E0B; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .info-box {{ background: white; border-left: 4px solid #F59E0B; padding: 15px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #F59E0B; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>Напоминание о сессии</h1></div>
                <div class="content">
                    <h2>Привет, {safe_username}!</h2>
                    <p>Ваша сессия состоится завтра:</p>
                    <div class="info-box">
                        <p><strong>Ментор:</strong> {safe_mentor_name}</p>
                        <p><strong>Дата:</strong> {safe_session_date}</p>
                    </div>
                    <div style="text-align: center;">
                        <a href="{session_link}" class="button">Присоединиться</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return self.send_email(to_email=to_email, subject=f"Напоминание: сессия завтра с {mentor_name}", html_content=html_content)

    def send_new_message_notification(
        self,
        to_email: str,
        username: str,
        sender_name: str,
        message_preview: str
    ) -> bool:
        """Уведомление о новом сообщении"""
        safe_username = html_lib.escape(username)
        safe_sender_name = html_lib.escape(sender_name)
        safe_message_preview = html_lib.escape(message_preview)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10B981; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .message-box {{ background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #10B981; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #10B981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>Новое сообщение</h1></div>
                <div class="content">
                    <h2>Привет, {safe_username}!</h2>
                    <p>Вам пришло новое сообщение от <strong>{safe_sender_name}</strong>:</p>
                    <div class="message-box">
                        <p style="color: #6b7280; font-style: italic;">"{safe_message_preview}..."</p>
                    </div>
                    <div style="text-align: center;">
                        <a href="{settings.FRONTEND_URL}/messages" class="button">Открыть сообщения</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return self.send_email(to_email=to_email, subject=f"Новое сообщение от {sender_name}", html_content=html_content)

    def send_course_enrollment_notification(
        self,
        to_email: str,
        username: str,
        course_name: str,
        instructor_name: str
    ) -> bool:
        """Уведомление о записи на курс"""
        safe_username = html_lib.escape(username)
        safe_course_name = html_lib.escape(course_name)
        safe_instructor_name = html_lib.escape(instructor_name)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #3B82F6; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .course-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #3B82F6; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>Запись на курс</h1></div>
                <div class="content">
                    <h2>Привет, {safe_username}!</h2>
                    <p>Вы успешно записались на курс:</p>
                    <div class="course-info">
                        <h3 style="margin-top: 0;">{safe_course_name}</h3>
                        <p><strong>Инструктор:</strong> {safe_instructor_name}</p>
                    </div>
                    <div style="text-align: center;">
                        <a href="{settings.FRONTEND_URL}/learning" class="button">Начать обучение</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return self.send_email(to_email=to_email, subject=f"Запись на курс: {course_name}", html_content=html_content)

    def send_payment_confirmation(
        self,
        to_email: str,
        username: str,
        amount: float,
        currency: str,
        transaction_id: str,
        service_name: str
    ) -> bool:
        """Подтверждение платежа"""
        safe_username = html_lib.escape(username)
        safe_service_name = html_lib.escape(service_name)
        safe_transaction_id = html_lib.escape(transaction_id)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #8B5CF6; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .payment-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .success {{ color: #10B981; font-size: 24px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>Платёж подтверждён</h1></div>
                <div class="content">
                    <h2>Спасибо за оплату, {safe_username}!</h2>
                    <div class="success">&#10003;</div>
                    <div class="payment-info">
                        <p><strong>Сумма:</strong> {amount} {currency}</p>
                        <p><strong>Услуга:</strong> {safe_service_name}</p>
                        <p><strong>ID транзакции:</strong> {safe_transaction_id}</p>
                    </div>
                    <p>Чек был сохранён в вашем профиле.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return self.send_email(to_email=to_email, subject=f"Подтверждение платежа {amount} {currency}", html_content=html_content)

    def send_achievement_unlocked(
        self,
        to_email: str,
        username: str,
        achievement_name: str,
        achievement_description: str
    ) -> bool:
        """Уведомление о полученном достижении"""
        safe_username = html_lib.escape(username)
        safe_achievement_name = html_lib.escape(achievement_name)
        safe_achievement_description = html_lib.escape(achievement_description)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #8B5CF6; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9fafb; }}
                .badge {{ background: #8B5CF6; color: white; padding: 10px 20px; border-radius: 20px; display: inline-block; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>Новое достижение!</h1></div>
                <div class="content">
                    <h2>Поздравляем, {safe_username}!</h2>
                    <p>Вы получили новое достижение:</p>
                    <div class="badge">{safe_achievement_name}</div>
                    <p>{safe_achievement_description}</p>
                    <p>Продолжайте в том же духе!</p>
                </div>
            </div>
        </body>
        </html>
        """
        return self.send_email(to_email=to_email, subject=f"Достижение разблокировано: {achievement_name}", html_content=html_content)


# Singleton instance
email_service = EmailService()
