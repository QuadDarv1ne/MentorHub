"""
Автоматическое резервное копирование базы данных
Использование: python backup_database.py
"""

import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Управление резервными копиями базы данных"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.s3_enabled = all([
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            settings.AWS_S3_BUCKET
        ])
        
        if self.s3_enabled:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=getattr(settings, 'AWS_REGION', 'eu-west-1')
            )
    
    def create_backup(self) -> Path:
        """Создание резервной копии базы данных"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"mentorhub_backup_{timestamp}.sql"
        
        logger.info(f"📦 Создание резервной копии: {backup_file}")
        
        # Парсинг DATABASE_URL
        db_url = settings.DATABASE_URL
        
        if db_url.startswith('sqlite'):
            # SQLite backup
            db_path = db_url.replace('sqlite:///', '')
            import shutil
            shutil.copy2(db_path, backup_file.with_suffix('.db'))
            backup_file = backup_file.with_suffix('.db')
            logger.info("✅ SQLite копия создана")
        
        elif db_url.startswith('postgresql'):
            # PostgreSQL backup
            try:
                # Извлечение параметров подключения
                from urllib.parse import urlparse
                parsed = urlparse(db_url)
                
                env = os.environ.copy()
                env['PGPASSWORD'] = parsed.password or ''
                
                cmd = [
                    'pg_dump',
                    '-h', parsed.hostname or 'localhost',
                    '-p', str(parsed.port or 5432),
                    '-U', parsed.username or 'postgres',
                    '-d', parsed.path.lstrip('/'),
                    '-F', 'c',  # Custom format (compressed)
                    '-f', str(backup_file)
                ]
                
                subprocess.run(cmd, check=True, env=env)
                logger.info("✅ PostgreSQL копия создана")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Ошибка создания backup: {e}")
                raise
            except Exception as e:
                logger.error(f"❌ Ошибка: {e}")
                raise
        
        else:
            raise ValueError(f"Неподдерживаемая база данных: {db_url}")
        
        # Получение размера файла
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        logger.info(f"📊 Размер backup: {size_mb:.2f} MB")
        
        return backup_file
    
    def upload_to_s3(self, backup_file: Path) -> bool:
        """Загрузка backup в S3"""
        if not self.s3_enabled:
            logger.warning("⚠️ S3 не настроен, пропуск загрузки")
            return False
        
        try:
            s3_key = f"backups/{backup_file.name}"
            
            logger.info(f"☁️ Загрузка в S3: s3://{settings.AWS_S3_BUCKET}/{s3_key}")
            
            self.s3_client.upload_file(
                str(backup_file),
                settings.AWS_S3_BUCKET,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'StorageClass': 'STANDARD_IA'  # Infrequent Access (дешевле)
                }
            )
            
            logger.info("✅ Успешно загружено в S3")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Ошибка загрузки в S3: {e}")
            return False
    
    def cleanup_old_backups(self, keep_days: int = 7):
        """Удаление старых локальных backup'ов"""
        logger.info(f"🧹 Очистка backup'ов старше {keep_days} дней")
        
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob("mentorhub_backup_*"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                deleted_count += 1
                logger.info(f"🗑️ Удалён: {backup_file.name}")
        
        logger.info(f"✅ Удалено {deleted_count} старых backup'ов")
    
    def restore_backup(self, backup_file: Path):
        """Восстановление из резервной копии"""
        logger.warning(f"⚠️ ВОССТАНОВЛЕНИЕ ИЗ BACKUP: {backup_file}")
        logger.warning("⚠️ Все текущие данные будут ПЕРЕЗАПИСАНЫ!")
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup файл не найден: {backup_file}")
        
        db_url = settings.DATABASE_URL
        
        if db_url.startswith('sqlite'):
            # SQLite restore
            db_path = db_url.replace('sqlite:///', '')
            import shutil
            
            # Создание backup текущей БД
            current_backup = f"{db_path}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_path, current_backup)
            logger.info(f"💾 Текущая БД сохранена в: {current_backup}")
            
            # Восстановление
            shutil.copy2(backup_file, db_path)
            logger.info("✅ SQLite восстановлена")
        
        elif db_url.startswith('postgresql'):
            # PostgreSQL restore
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            
            env = os.environ.copy()
            env['PGPASSWORD'] = parsed.password or ''
            
            cmd = [
                'pg_restore',
                '-h', parsed.hostname or 'localhost',
                '-p', str(parsed.port or 5432),
                '-U', parsed.username or 'postgres',
                '-d', parsed.path.lstrip('/'),
                '-c',  # Clean (drop) database objects before recreating
                '-F', 'c',  # Custom format
                str(backup_file)
            ]
            
            try:
                subprocess.run(cmd, check=True, env=env)
                logger.info("✅ PostgreSQL восстановлена")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Ошибка восстановления: {e}")
                raise
        
        else:
            raise ValueError(f"Неподдерживаемая база данных: {db_url}")


def main():
    """Главная функция для запуска backup"""
    backup = DatabaseBackup()
    
    try:
        # 1. Создание backup
        backup_file = backup.create_backup()
        
        # 2. Загрузка в S3 (если настроен)
        backup.upload_to_s3(backup_file)
        
        # 3. Очистка старых backup'ов
        backup.cleanup_old_backups(keep_days=7)
        
        logger.info("🎉 Backup успешно завершён!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка выполнения backup: {e}")
        raise


if __name__ == "__main__":
    main()
