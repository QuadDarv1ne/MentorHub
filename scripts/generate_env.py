#!/usr/bin/env python3
"""
MentorHub - Intelligent Environment Configuration Generator
Автоматическая генерация и валидация .env файла
Platforms: Cross-platform (Linux, macOS, Windows)
"""

import os
import sys
import socket
import secrets
import string
import platform
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class PortConfig:
    """Конфигурация портов"""
    backend: int = 8000
    frontend: int = 3000
    database: int = 5432
    redis: int = 6379
    nginx_http: int = 80
    nginx_https: int = 443
    prometheus: int = 9090
    grafana: int = 3001


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных"""
    user: str = "mentorhub_user"
    name: str = "mentorhub_dev"
    password: str = ""
    pool_size: int = 20
    max_overflow: int = 40
    echo: bool = False


@dataclass
class JWTConfig:
    """JWT конфигурация"""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


@dataclass
class EnvironmentConfig:
    """Полная конфигурация окружения"""
    app_name: str = "MentorHub API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    host: str = "0.0.0.0"
    ports: PortConfig = None
    database: DatabaseConfig = None
    jwt: JWTConfig = None
    cors_origins: str = ""
    agora_app_id: str = ""
    agora_app_certificate: str = ""
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@mentorhub.com"
    sentry_dsn: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = "mentorhub-bucket"
    grafana_admin_user: str = "admin"
    grafana_admin_password: str = "admin"

    def __post_init__(self):
        if self.ports is None:
            self.ports = PortConfig()
        if self.database is None:
            self.database = DatabaseConfig()
        if self.jwt is None:
            self.jwt = JWTConfig()


class PortChecker:
    """Проверка доступности портов"""
    
    @staticmethod
    def is_port_available(port: int, host: str = '127.0.0.1') -> bool:
        """Проверяет доступность порта"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                return result != 0
        except Exception:
            return True  # Если не удалось проверить, считаем порт свободным
    
    @staticmethod
    def find_free_port(base_port: int, max_attempts: int = 100) -> Optional[int]:
        """Находит первый свободный порт начиная с базового"""
        for i in range(max_attempts):
            port = base_port + i
            if PortChecker.is_port_available(port):
                return port
        return None


class EnvironmentGenerator:
    """Генератор конфигурации окружения"""
    
    def __init__(self, project_dir: Path, environment: str = "development"):
        self.project_dir = project_dir
        self.environment = environment
        self.is_root = self._check_root()
        
    def _check_root(self) -> bool:
        """Проверяет запущен ли скрипт от root"""
        if platform.system() == "Windows":
            import ctypes
            try:
                return bool(ctypes.windll.shell32.IsUserAnAdmin())
            except Exception:
                return False
        else:
            return os.geteuid() == 0
    
    def generate_secret_key(self, length: int = 64) -> str:
        """Генерирует безопасный секретный ключ"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    def generate_password(self, length: int = 20) -> str:
        """Генерирует безопасный пароль"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Гарантируем наличие хотя бы одной цифры и специального символа
        if not any(c.isdigit() for c in password):
            password = password[:-1] + secrets.choice(string.digits)
        if not any(c in "!@#$%^&*" for c in password):
            password = password[:-2] + secrets.choice("!@#$%^&*") + password[-1]
        return password
    
    def detect_ports(self) -> PortConfig:
        """Автоопределение свободных портов"""
        ports = PortConfig()
        
        # Backend port
        if not PortChecker.is_port_available(ports.backend):
            free_port = PortChecker.find_free_port(ports.backend)
            if free_port:
                ports.backend = free_port
        
        # Frontend port
        if not PortChecker.is_port_available(ports.frontend):
            free_port = PortChecker.find_free_port(ports.frontend)
            if free_port:
                ports.frontend = free_port
        
        # Database port
        if not PortChecker.is_port_available(ports.database):
            free_port = PortChecker.find_free_port(ports.database)
            if free_port:
                ports.database = free_port
        
        # Redis port
        if not PortChecker.is_port_available(ports.redis):
            free_port = PortChecker.find_free_port(ports.redis)
            if free_port:
                ports.redis = free_port
        
        # Nginx ports (требуют root для < 1024)
        if not self.is_root:
            ports.nginx_http = 8080 if PortChecker.is_port_available(8080) else PortChecker.find_free_port(8080) or 8080
            ports.nginx_https = 8443 if PortChecker.is_port_available(8443) else PortChecker.find_free_port(8443) or 8443
        else:
            if not PortChecker.is_port_available(ports.nginx_http):
                free_port = PortChecker.find_free_port(ports.nginx_http)
                if free_port:
                    ports.nginx_http = free_port
            
            if not PortChecker.is_port_available(ports.nginx_https):
                free_port = PortChecker.find_free_port(ports.nginx_https)
                if free_port:
                    ports.nginx_https = free_port
        
        # Prometheus port
        if not PortChecker.is_port_available(ports.prometheus):
            free_port = PortChecker.find_free_port(ports.prometheus)
            if free_port:
                ports.prometheus = free_port
        
        # Grafana port
        if not PortChecker.is_port_available(ports.grafana):
            free_port = PortChecker.find_free_port(ports.grafana)
            if free_port:
                ports.grafana = free_port
        
        return ports
    
    def generate_cors_origins(self, ports: PortConfig) -> str:
        """Генерирует CORS origins"""
        origins = [
            f"http://localhost:{ports.frontend}",
            f"http://localhost:{ports.backend}",
            f"http://127.0.0.1:{ports.frontend}",
            f"http://127.0.0.1:{ports.backend}",
        ]
        return ",".join(origins)
    
    def generate_config(self) -> EnvironmentConfig:
        """Генерирует полную конфигурацию"""
        print("🔍 Определение системных ресурсов...")
        ports = self.detect_ports()
        
        print("🔑 Генерация секретных ключей...")
        secret_key = self.generate_secret_key(64)
        db_password = self.generate_password(20)
        
        print("⚙️  Создание конфигурации...")
        config = EnvironmentConfig(
            environment=self.environment,
            ports=ports,
            database=DatabaseConfig(
                password=db_password
            ),
            jwt=JWTConfig(),
            cors_origins=self.generate_cors_origins(ports),
        )
        
        # Показываем информацию о портах
        print("\n📡 Конфигурация портов:")
        print(f"   Backend:      {ports.backend}")
        print(f"   Frontend:     {ports.frontend}")
        print(f"   Database:     {ports.database}")
        print(f"   Redis:        {ports.redis}")
        print(f"   Nginx HTTP:   {ports.nginx_http}")
        print(f"   Nginx HTTPS:  {ports.nginx_https}")
        print(f"   Prometheus:   {ports.prometheus}")
        print(f"   Grafana:      {ports.grafana}")
        
        return config
    
    def generate_env_content(self, config: EnvironmentConfig) -> str:
        """Генерирует содержимое .env файла"""
        db_password_escaped = config.database.password.replace('\\', '\\\\').replace('$', '\\$')
        
        env_content = f"""# =====================================================
# MentorHub - Auto-generated Configuration
# Generated: {platform.system()} {platform.release()}
# Environment: {config.environment}
# =====================================================

# ==================== APPLICATION ====================
APP_NAME={config.app_name}
APP_VERSION={config.app_version}
DEBUG={config.debug}
ENVIRONMENT={config.environment}

# ==================== SERVER ====================
HOST={config.host}
PORT={config.ports.backend}

# ==================== PORTS ====================
BACKEND_PORT={config.ports.backend}
FRONTEND_PORT={config.ports.frontend}
DB_PORT={config.ports.database}
REDIS_PORT={config.ports.redis}
NGINX_HTTP_PORT={config.ports.nginx_http}
NGINX_HTTPS_PORT={config.ports.nginx_https}
PROMETHEUS_PORT={config.ports.prometheus}
GRAFANA_PORT={config.ports.grafana}

# ==================== DATABASE ====================
DB_USER={config.database.user}
DB_PASSWORD={db_password_escaped}
DB_NAME={config.database.name}
DATABASE_URL=postgresql://${{DB_USER}}:${{DB_PASSWORD}}@localhost:${{DB_PORT}}/${{DB_NAME}}
DB_ECHO={config.database.echo}
DB_POOL_SIZE={config.database.pool_size}
DB_MAX_OVERFLOW={config.database.max_overflow}

# ==================== REDIS ====================
REDIS_URL=redis://localhost:${{REDIS_PORT}}/0
REDIS_HOST=localhost
REDIS_PORT=${{REDIS_PORT}}
REDIS_DB=0

# ==================== JWT AUTHENTICATION ====================
SECRET_KEY={config.jwt.algorithm}
ALGORITHM={config.jwt.access_token_expire_minutes}
ACCESS_TOKEN_EXPIRE_MINUTES={config.jwt.refresh_token_expire_days}
REFRESH_TOKEN_EXPIRE_DAYS=7

# ==================== CORS ====================
CORS_ORIGINS={config.cors_origins}

# ==================== AGORA VIDEO ====================
AGORA_APP_ID={config.agora_app_id or 'your-agora-app-id'}
AGORA_APP_CERTIFICATE={config.agora_app_certificate or 'your-agora-certificate'}

# ==================== STRIPE PAYMENTS ====================
STRIPE_API_KEY={config.stripe_api_key or 'your-stripe-api-key'}
STRIPE_SECRET_KEY={config.stripe_api_key or 'your-stripe-secret-key'}
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET={config.stripe_webhook_secret or 'your-stripe-webhook-secret'}
STRIPE_MOCK_MODE=True

# ==================== SBP (SISTEMA BYSTRYKH PLATEZHEY) ====================
SBP_MERCHANT_ID=your-sbp-merchant-id
SBP_API_KEY=your-sbp-api-key
SBP_API_SECRET=your-sbp-api-secret
SBP_CALLBACK_URL=http://localhost:${{BACKEND_PORT}}/api/payments/sbp/callback
SBP_MOCK_MODE=True

# ==================== EMAIL ====================
SMTP_HOST={config.smtp_host}
SMTP_PORT={config.smtp_port}
SMTP_USER={config.smtp_user or 'your-email@gmail.com'}
SMTP_PASSWORD={config.smtp_password or 'your-app-password'}
SMTP_FROM_EMAIL={config.smtp_from_email}
SMTP_FROM_NAME=MentorHub

# ==================== FRONTEND ====================
NEXT_PUBLIC_API_BASE_URL=http://localhost:${{BACKEND_PORT}}/api/v1
NEXT_PUBLIC_SITE_URL=http://localhost:${{FRONTEND_PORT}}
NEXT_PUBLIC_API_URL=http://localhost:${{BACKEND_PORT}}

# ==================== MONITORING ====================
GRAFANA_ADMIN_USER={config.grafana_admin_user}
GRAFANA_ADMIN_PASSWORD={config.grafana_admin_password}

# ==================== OPTIONAL ====================
SENTRY_DSN={config.sentry_dsn}
TELEGRAM_BOT_TOKEN={config.telegram_bot_token}
TELEGRAM_CHAT_ID={config.telegram_chat_id}
AWS_ACCESS_KEY_ID={config.aws_access_key_id}
AWS_SECRET_ACCESS_KEY={config.aws_secret_access_key}
AWS_S3_BUCKET={config.aws_s3_bucket}
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
"""
        return env_content
    
    def save_config(self, config: EnvironmentConfig, output_file: Path):
        """Сохраняет конфигурацию в файл"""
        env_content = self.generate_env_content(config)
        
        output_file.write_text(env_content, encoding='utf-8')
        print(f"\n✅ Конфигурация сохранена в: {output_file}")
        
        # Показываем URLs
        print("\n📍 Services URLs:")
        print(f"   Backend API:    http://localhost:{config.ports.backend}")
        print(f"   API Docs:       http://localhost:{config.ports.backend}/docs")
        print(f"   Frontend:       http://localhost:{config.ports.frontend}")
        print(f"   Database:       localhost:{config.ports.database}")
        print(f"   Redis:          localhost:{config.ports.redis}")
        print(f"   Grafana:        http://localhost:{config.ports.grafana}")
        
        print("\n🚀 Теперь запустите:")
        print("   make docker-up  или  docker-compose up -d")


class EnvironmentValidator:
    """Валидатор конфигурации"""
    
    def __init__(self, env_file: Path):
        self.env_file = env_file
        self.errors = []
        self.warnings = []
    
    def validate(self) -> bool:
        """Валидирует .env файл"""
        if not self.env_file.exists():
            print(f"❌ .env файл не найден: {self.env_file}")
            return False
        
        env_vars = self._load_env_file()
        
        # Обязательные переменные
        required_vars = [
            'SECRET_KEY', 'DB_PASSWORD', 'DB_USER', 'DB_NAME',
            'DATABASE_URL', 'REDIS_URL'
        ]
        
        for var in required_vars:
            if var not in env_vars:
                self.errors.append(f"Отсутствует обязательная переменная: {var}")
            elif not env_vars[var] or env_vars[var].startswith('your-') or env_vars[var].startswith('change-'):
                self.errors.append(f"Переменная {var} не настроена (используется placeholder)")
        
        # Проверка SECRET_KEY
        if 'SECRET_KEY' in env_vars:
            if len(env_vars['SECRET_KEY']) < 32:
                self.errors.append("SECRET_KEY слишком короткий (минимум 32 символа)")
            elif env_vars['SECRET_KEY'] in ['change-this-secret-key-in-production-use-openssl-rand-hex-32', 
                                              'your-secret-key', 'change-me']:
                self.errors.append("SECRET_KEY использует значение по умолчанию")
        
        # Проверка DB_PASSWORD
        if 'DB_PASSWORD' in env_vars:
            if env_vars['DB_PASSWORD'] in ['change-this-password-in-production', 'password', 'SECURE_PASSWORD']:
                self.errors.append("DB_PASSWORD использует значение по умолчанию")
            elif len(env_vars['DB_PASSWORD']) < 8:
                self.errors.append("DB_PASSWORD слишком короткий (минимум 8 символов)")
        
        # Проверка CORS
        if 'CORS_ORIGINS' in env_vars:
            if not env_vars['CORS_ORIGINS']:
                self.warnings.append("CORS_ORIGINS пуст - это может вызвать проблемы с CORS")
        
        # Проверка портов
        port_vars = ['BACKEND_PORT', 'FRONTEND_PORT', 'DB_PORT', 'REDIS_PORT']
        for port_var in port_vars:
            if port_var in env_vars:
                try:
                    port = int(env_vars[port_var])
                    if port < 1 or port > 65535:
                        self.errors.append(f"{port_var} вне диапазона (1-65535)")
                except ValueError:
                    self.errors.append(f"{port_var} не является числом")
        
        # Вывод результатов
        if self.errors:
            print("\n❌ Ошибки валидации:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print("\n⚠️  Предупреждения:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.errors:
            print("\n✅ Валидация прошла успешно!")
            return True
        else:
            print(f"\n❌ Найдено ошибок: {len(self.errors)}")
            return False
    
    def _load_env_file(self) -> Dict[str, str]:
        """Загружает .env файл"""
        env_vars = {}
        content = self.env_file.read_text(encoding='utf-8')
        
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
        
        return env_vars


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MentorHub Environment Configuration Generator')
    parser.add_argument('--mode', choices=['development', 'production', 'staging'], 
                       default='development', help='Режим окружения')
    parser.add_argument('--output', type=str, default='.env', 
                       help='Выходной файл (по умолчанию: .env)')
    parser.add_argument('--validate', type=str, default='.env',
                       help='Валидировать существующий .env файл')
    parser.add_argument('--force', action='store_true',
                       help='Перезаписать существующий файл')
    
    args = parser.parse_args()
    
    project_dir = Path(__file__).parent.parent
    
    # Режим валидации
    if args.validate:
        print("🔍 Валидация конфигурации...")
        validator = EnvironmentValidator(project_dir / args.validate)
        success = validator.validate()
        sys.exit(0 if success else 1)
    
    # Режим генерации
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   🔧 MentorHub Environment Generator                       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    output_file = project_dir / args.output
    
    # Проверка на существующий файл
    if output_file.exists() and not args.force:
        print(f"⚠️  Файл {output_file} уже существует")
        print("   Используйте --force для перезаписи")
        print("   Или укажите другой файл через --output")
        sys.exit(1)
    
    # Генерация конфигурации
    generator = EnvironmentGenerator(project_dir, args.mode)
    config = generator.generate_config()
    
    # Сохранение
    generator.save_config(config, output_file)
    
    print("\n✅ Готово!")


if __name__ == "__main__":
    main()
