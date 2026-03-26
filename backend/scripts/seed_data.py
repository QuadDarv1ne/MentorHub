#!/usr/bin/env python3
"""
Скрипт для заполнения БД тестовыми данными
"""
import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
import random

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
from app.models.mentor import Mentor
from app.models.course import Course
from app.utils.security import get_password_hash


SKILLS = ["Python", "JavaScript", "React", "Django", "FastAPI", "PostgreSQL", "Docker", "AWS"]
COURSES = [
    ("Python для начинающих", "Базовый курс Python", "beginner", 40, 15000),
    ("Web разработка с Django", "Полный курс Django", "intermediate", 60, 25000),
    ("FastAPI микросервисы", "Создание API с FastAPI", "advanced", 35, 20000),
    ("React и TypeScript", "Современный фронтенд", "intermediate", 50, 22000),
]


def seed_data():
    """Заполнить БД тестовыми данными"""
    db = SessionLocal()

    try:
        logger.info("🌱 Заполнение БД тестовыми данными...")
        logger.info("-" * 50)

        # Создаем тестовых пользователей
        users = []
        for i in range(1, 6):
            user = User(
                email=f"user{i}@example.com",
                hashed_password=get_password_hash("password123"),
                full_name=f"Тестовый Пользователь {i}",
                role="student" if i <= 3 else "mentor",
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            users.append(user)

        db.commit()
        print(f"✅ Создано {len(users)} пользователей")

        # Создаем менторов
        mentors = []
        for user in users[3:]:  # Последние 2 пользователя - менторы
            mentor = Mentor(
                user_id=user.id,
                title=f"Senior Developer",
                description=f"Опытный разработчик с {random.randint(5, 15)} годами опыта",
                skills=random.sample(SKILLS, k=random.randint(3, 5)),
                price_per_hour=random.randint(2000, 5000),
                rating=round(random.uniform(4.0, 5.0), 1),
                total_sessions=random.randint(50, 200),
                is_available=True,
            )
            db.add(mentor)
            mentors.append(mentor)

        db.commit()
        print(f"✅ Создано {len(mentors)} менторов")

        # Создаем курсы
        courses = []
        for title, desc, level, hours, price in COURSES:
            course = Course(
                title=title,
                description=desc,
                category="programming",
                level=level,
                duration_hours=hours,
                price=price,
                rating=round(random.uniform(4.0, 5.0), 1),
                students_count=random.randint(100, 500),
            )
            db.add(course)
            courses.append(course)

        db.commit()
        print(f"✅ Создано {len(courses)} курсов")

        print("\n" + "=" * 50)
        print("✅ База данных успешно заполнена тестовыми данными!")
        print("=" * 50)
        print("\n📝 Тестовые пользователи:")
        print("  Email: user1@example.com | Пароль: password123")
        print("  Email: user2@example.com | Пароль: password123")
        print("  Email: user3@example.com | Пароль: password123")
        print("\n🎓 Тестовые менторы:")
        print("  Email: user4@example.com | Пароль: password123")
        print("  Email: user5@example.com | Пароль: password123")
        print("=" * 50)

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
