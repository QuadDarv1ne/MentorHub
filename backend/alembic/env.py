"""
Конфигурация окружения Alembic
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# Добавление родительской директории в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from app.database import Base

# Импортируйте все модели здесь для обнаружения Alembic
from app.models import (  # noqa
    Achievement,
    Course,
    CourseEnrollment,
    DeviceToken,
    Lesson,
    Mentor,
    Message,
    Notification,
    Payment,
    Progress,
    Review,
    Session,
    User,
)

# Это объект конфигурации Alembic, который предоставляет
# доступ к значениям в используемом .ini файле.
config = context.config

# Интерпретация файла конфигурации для логирования Python.
# Эта строка настраивает логирование.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Установка URL базы данных из настроек
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Добавьте объект MetaData ваших моделей здесь
# для поддержки 'autogenerate'
target_metadata = Base.metadata

# Другие значения из конфигурации, определенные потребностями env.py,
# могут быть получены:
# my_important_option = config.get_main_option("my_important_option")
# ... и т.д.


def run_migrations_offline() -> None:
    """Запуск миграций в режиме 'offline'.

    Это настраивает контекст только с URL
    и без Engine, хотя Engine здесь тоже допустим.
    Пропуская создание Engine,
    нам даже не нужен доступный DBAPI.

    Вызовы context.execute() здесь выводят данную строку
    в выходной скрипт.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в режиме 'online'.

    В этом сценарии нам нужно создать Engine
    и связать соединение с контекстом.

    """
    # Создаем Engine из URL базы данных
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,  # Не используем пул для миграций
        echo=settings.DEBUG,  # Логирование SQL только в debug режиме
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Включаем batch mode для SQLite
            compare_type=True,  # Сравниваем типы колонок
            compare_server_default=True,  # Сравниваем значения по умолчанию
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
