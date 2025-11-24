"""
Конфигурация окружения Alembic
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Добавление родительской директории в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.config import settings

# Импортируйте все модели здесь для обнаружения Alembic
from app.models import User, Mentor, Session, Message, Payment  # noqa

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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
