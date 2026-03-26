#!/usr/bin/env python3
"""
Проверка переменных окружения перед запуском
"""
import os
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("🔍 Проверка переменных окружения")
logger.info("=" * 60)

required_vars = {
    "DATABASE_URL": "Строка подключения к PostgreSQL",
    "SECRET_KEY": "Секретный ключ для JWT",
}

optional_vars = {
    "REDIS_URL": "Строка подключения к Redis",
    "ENVIRONMENT": "Окружение (production/development)",
    "PORT": "Порт приложения",
}

errors = []
warnings = []

# Проверка обязательных переменных
for var, description in required_vars.items():
    value = os.environ.get(var)
    if not value:
        errors.append(f"❌ {var} - {description}")
        logger.error(f"❌ {var}: НЕ УСТАНОВЛЕНА")
    else:
        # Скрываем чувствительные данные
        if "PASSWORD" in var or "SECRET" in var or "KEY" in var:
            masked = value[:10] + "..." if len(value) > 10 else "***"
            logger.info(f"✅ {var}: {masked}")
        elif "URL" in var:
            # Показываем только протокол и хост
            masked = value.split("@")[-1] if "@" in value else value[:30] + "..."
            logger.info(f"✅ {var}: ...@{masked}")
        else:
            logger.info(f"✅ {var}: {value}")

# Проверка опциональных переменных
logger.info("\n📋 Опциональные переменные:")
for var, description in optional_vars.items():
    value = os.environ.get(var)
    if not value:
        warnings.append(f"⚠️  {var} - {description}")
        logger.warning(f"⚠️  {var}: не установлена")
    else:
        logger.info(f"✅ {var}: {value}")

logger.info("=" * 60)

if errors:
    logger.error("\n❌ КРИТИЧЕСКИЕ ОШИБКИ:")
    for error in errors:
        logger.error(f"  {error}")
    logger.error("\n💡 Установите переменные окружения в настройках Amvera")
    sys.exit(1)

if warnings:
    logger.warning("\n⚠️  ПРЕДУПРЕЖДЕНИЯ:")
    for warning in warnings:
        logger.warning(f"  {warning}")

logger.info("\n✅ Все обязательные переменные установлены!")
logger.info("🚀 Запуск приложения...\n")
sys.exit(0)
