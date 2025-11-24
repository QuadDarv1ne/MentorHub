#!/usr/bin/env python3
"""
Проверка переменных окружения перед запуском
"""
import os
import sys

print("=" * 60)
print("🔍 Проверка переменных окружения")
print("=" * 60)

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
        print(f"❌ {var}: НЕ УСТАНОВЛЕНА")
    else:
        # Скрываем чувствительные данные
        if "PASSWORD" in var or "SECRET" in var or "KEY" in var:
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"✅ {var}: {masked}")
        elif "URL" in var:
            # Показываем только протокол и хост
            masked = value.split("@")[-1] if "@" in value else value[:30] + "..."
            print(f"✅ {var}: ...@{masked}")
        else:
            print(f"✅ {var}: {value}")

# Проверка опциональных переменных
print("\n📋 Опциональные переменные:")
for var, description in optional_vars.items():
    value = os.environ.get(var)
    if not value:
        warnings.append(f"⚠️  {var} - {description}")
        print(f"⚠️  {var}: не установлена")
    else:
        print(f"✅ {var}: {value}")

print("=" * 60)

if errors:
    print("\n❌ КРИТИЧЕСКИЕ ОШИБКИ:")
    for error in errors:
        print(f"  {error}")
    print("\n💡 Установите переменные окружения в настройках Amvera")
    sys.exit(1)

if warnings:
    print("\n⚠️  ПРЕДУПРЕЖДЕНИЯ:")
    for warning in warnings:
        print(f"  {warning}")

print("\n✅ Все обязательные переменные установлены!")
print("🚀 Запуск приложения...\n")
sys.exit(0)
