#!/usr/bin/env python3
"""
Скрипт для создания первого пользователя-администратора
"""
import sys
import os
from pathlib import Path

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
            print(f"❌ Администратор уже существует: {existing_admin.email}")
            return

        # Запрашиваем данные
        print("📝 Создание администратора MentorHub")
        print("-" * 50)

        email = input("Email: ").strip()
        if not email:
            print("❌ Email обязателен!")
            return

        password = input("Пароль: ").strip()
        if not password or len(password) < 8:
            print("❌ Пароль должен быть не менее 8 символов!")
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

        print("\n" + "=" * 50)
        print("✅ Администратор успешно создан!")
        print("=" * 50)
        print(f"📧 Email: {admin.email}")
        print(f"👤 Имя: {admin.full_name}")
        print(f"🔑 ID: {admin.id}")
        print("=" * 50)

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
