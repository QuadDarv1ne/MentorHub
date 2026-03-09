"""
Background tasks using Celery
Асинхронные задачи для email, уведомлений, аналитики
"""

import logging
from datetime import datetime, timedelta
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.utils.email import email_service

logger = logging.getLogger(__name__)

# Инициализация Celery
celery_app = Celery(
    "mentorhub",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
)

# Database session для tasks
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(name="send_verification_email_task")
def send_verification_email_task(email: str, username: str, token: str):
    """
    Асинхронная отправка email с подтверждением
    
    Args:
        email: Email получателя
        username: Имя пользователя
        token: Токен подтверждения
    """
    try:
        success = email_service.send_verification_email(email, username, token)
        if success:
            logger.info(f"✅ Verification email sent to {email}")
        else:
            logger.error(f"❌ Failed to send verification email to {email}")
        return success
    except Exception as e:
        logger.error(f"❌ Error sending verification email: {e}")
        raise


@celery_app.task(name="send_password_reset_email_task")
def send_password_reset_email_task(email: str, username: str, token: str):
    """
    Асинхронная отправка email для сброса пароля
    
    Args:
        email: Email получателя
        username: Имя пользователя
        token: Токен сброса пароля
    """
    try:
        success = email_service.send_password_reset_email(email, username, token)
        if success:
            logger.info(f"✅ Password reset email sent to {email}")
        else:
            logger.error(f"❌ Failed to send password reset email to {email}")
        return success
    except Exception as e:
        logger.error(f"❌ Error sending password reset email: {e}")
        raise


@celery_app.task(name="send_session_reminder_task")
def send_session_reminder_task(
    email: str,
    username: str,
    session_date: str,
    mentor_name: str,
    session_link: str
):
    """
    Отправка напоминания о предстоящей сессии
    
    Args:
        email: Email студента
        username: Имя студента
        session_date: Дата и время сессии
        mentor_name: Имя ментора
        session_link: Ссылка на сессию
    """
    try:
        success = email_service.send_session_notification(
            email, username, session_date, mentor_name, session_link
        )
        if success:
            logger.info(f"✅ Session reminder sent to {email}")
        else:
            logger.error(f"❌ Failed to send session reminder to {email}")
        return success
    except Exception as e:
        logger.error(f"❌ Error sending session reminder: {e}")
        raise


@celery_app.task(name="cleanup_expired_tokens")
def cleanup_expired_tokens():
    """
    Периодическая очистка истекших токенов
    Выполняется каждый день в 3:00
    """
    from app.api.email_verification import verification_tokens, reset_tokens
    
    try:
        current_time = datetime.utcnow()
        
        # Очистка verification tokens
        expired_verification = [
            token for token, data in verification_tokens.items()
            if current_time > data["expires_at"]
        ]
        for token in expired_verification:
            del verification_tokens[token]
        
        # Очистка reset tokens
        expired_reset = [
            token for token, data in reset_tokens.items()
            if current_time > data["expires_at"]
        ]
        for token in expired_reset:
            del reset_tokens[token]
        
        logger.info(
            f"✅ Cleaned up {len(expired_verification)} verification tokens "
            f"and {len(expired_reset)} reset tokens"
        )
        
        return {
            "verification_tokens_cleaned": len(expired_verification),
            "reset_tokens_cleaned": len(expired_reset)
        }
    except Exception as e:
        logger.error(f"❌ Error cleaning up tokens: {e}")
        raise


@celery_app.task(name="generate_daily_stats")
def generate_daily_stats():
    """
    Генерация ежедневной статистики
    Выполняется каждый день в 1:00
    """
    from app.models.user import User
    from app.models.session import Session
    from app.models.course import Course
    
    db = SessionLocal()
    try:
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Подсчет новых пользователей
        new_users = db.query(User).filter(
            User.created_at >= yesterday
        ).count()
        
        # Подсчет проведенных сессий
        completed_sessions = db.query(Session).filter(
            Session.status == "completed",
            Session.updated_at >= yesterday
        ).count()
        
        # Подсчет новых курсов
        new_courses = db.query(Course).filter(
            Course.created_at >= yesterday
        ).count()
        
        stats = {
            "date": yesterday.date().isoformat(),
            "new_users": new_users,
            "completed_sessions": completed_sessions,
            "new_courses": new_courses
        }
        
        logger.info(f"✅ Daily stats generated: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error generating daily stats: {e}")
        raise
    finally:
        db.close()


@celery_app.task(name="send_session_reminders")
def send_session_reminders():
    """
    Отправка напоминаний о предстоящих сессиях
    Выполняется каждый час
    """
    from app.models.session import Session, SessionStatus
    from app.models.user import User
    
    db = SessionLocal()
    try:
        # Ищем сессии, которые начнутся через 1 час
        one_hour_later = datetime.utcnow() + timedelta(hours=1)
        upcoming_sessions = db.query(Session).filter(
            Session.status == SessionStatus.SCHEDULED,
            Session.scheduled_at <= one_hour_later,
            Session.scheduled_at > datetime.utcnow()
        ).all()
        
        sent_count = 0
        for session in upcoming_sessions:
            student = db.query(User).filter(User.id == session.student_id).first()
            mentor = db.query(User).filter(
                User.mentor_profile.has(id=session.mentor_id)
            ).first()
            
            if student and mentor:
                session_link = f"{settings.FRONTEND_URL}/sessions/{session.id}"
                send_session_reminder_task.delay(
                    email=student.email,
                    username=student.username,
                    session_date=session.scheduled_at.strftime("%d.%m.%Y %H:%M"),
                    mentor_name=mentor.full_name or mentor.username,
                    session_link=session_link
                )
                sent_count += 1
        
        logger.info(f"✅ Sent {sent_count} session reminders")
        return {"reminders_sent": sent_count}
        
    except Exception as e:
        logger.error(f"❌ Error sending session reminders: {e}")
        raise
    finally:
        db.close()


# Периодические задачи (Celery Beat)
celery_app.conf.beat_schedule = {
    "cleanup-expired-tokens-daily": {
        "task": "cleanup_expired_tokens",
        "schedule": timedelta(days=1),  # Каждый день
    },
    "generate-daily-stats": {
        "task": "generate_daily_stats",
        "schedule": timedelta(days=1),  # Каждый день
    },
    "send-session-reminders-hourly": {
        "task": "send_session_reminders",
        "schedule": timedelta(hours=1),  # Каждый час
    },
}
