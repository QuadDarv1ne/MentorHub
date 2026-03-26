#!/usr/bin/env python3
"""
Скрипт для создания первого пользователя-администратора
"""
import sys
import os
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Добавляем backend в PYTHONPATH
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash
from sqlalchemy import select


def create_admin():
    """Создать администратора"""
    db = SessionLocal()

    try:
        # Проверяем, есть ли уже админ
        stmt = select(User).where(User.role == "admin")
        existing_admin = db.execute(stmt).scalar_one_or_none()

        if existing_admin:
            logger.error(f"❌ Администратор уже существует: {existing_admin.email}")
            return

        # Запрашиваем данные
        logger.info("📝 Создание администратора MentorHub")
        logger.info("-" * 50)

        email = input("Email: ").strip()
        if not email:
            logger.error("❌ Email обязателен!")
            return

        password = input("Пароль: ").strip()
        if not password or len(password) < 8:
            logger.error("❌ Пароль должен быть не менее 8 символов!")
            return

        full_name = input("Полное имя: ").strip() or "Administrator"

        # Создаем админа
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role="admin",
            is_active=True,
            is_verified=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        logger.info("\n" + "=" * 50)
        logger.info("✅ Администратор успешно создан!")
        logger.info("=" * 50)
        logger.info(f"📧 Email: {admin.email}")
        logger.info(f"👤 Имя: {admin.full_name}")
        logger.info(f"🔑 ID: {admin.id}")
        logger.info("=" * 50)

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Ошибка: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
