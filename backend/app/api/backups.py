"""
API endpoints для управления резервными копиями
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from pathlib import Path

from app.models.user import User
from app.dependencies import get_current_user
from app.config import settings

# Conditional import to avoid issues when backup module is not available
try:
    from backup_database import DatabaseBackup
    BACKUP_AVAILABLE = True
except ImportError:
    BACKUP_AVAILABLE = False
    DatabaseBackup = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/backups", tags=["backups"])


@router.get("/info", response_model=Dict[str, Any])
async def get_backup_info(current_user: User = Depends(get_current_user)):
    """
    Получение информации о резервных копиях
    Доступно только администраторам
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access backup info")

    if not BACKUP_AVAILABLE:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Backup functionality not available")

    try:
        backup_manager = DatabaseBackup()
        info = backup_manager.get_backup_info()
        return info
    except Exception as e:
        logger.error(f"Error getting backup info: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось получить информацию о backup'ах")


@router.post("/create", response_model=Dict[str, str])
async def create_backup(current_user: User = Depends(get_current_user)):
    """
    Создание резервной копии базы данных
    Доступно только администраторам
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can create backups")

    if not BACKUP_AVAILABLE:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Backup functionality not available")

    try:
        backup_manager = DatabaseBackup()
        backup_file = backup_manager.create_backup()
        
        # Upload to S3 if configured
        if backup_manager.s3_enabled:
            backup_manager.upload_to_s3(backup_file)
            
        return {"message": f"Резервная копия создана: {backup_file.name}", "filename": backup_file.name}
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось создать резервную копию")


@router.post("/cleanup", response_model=Dict[str, str])
async def cleanup_backups(keep_days: int = 7, current_user: User = Depends(get_current_user)):
    """
    Очистка старых резервных копий
    Доступно только администраторам
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can cleanup backups")

    if not BACKUP_AVAILABLE:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Backup functionality not available")

    try:
        backup_manager = DatabaseBackup()
        backup_manager.cleanup_old_backups(keep_days=keep_days)
        return {"message": f"Очистка backup'ов завершена. Удалены backup'ы старше {keep_days} дней"}
    except Exception as e:
        logger.error(f"Error cleaning up backups: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось выполнить очистку backup'ов")


@router.get("/verify/{filename}", response_model=Dict[str, Any])
async def verify_backup(filename: str, current_user: User = Depends(get_current_user)):
    """
    Проверка целостности резервной копии
    Доступно только администраторам
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can verify backups")

    if not BACKUP_AVAILABLE:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Backup functionality not available")

    try:
        backup_manager = DatabaseBackup()
        backup_file = Path("backups") / filename
        
        if not backup_file.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup файл не найден")
            
        # Проверяем целостность
        if filename in backup_manager.backup_metadata:
            expected_hash = backup_manager.backup_metadata[filename].get("hash")
            if expected_hash:
                actual_hash = backup_manager._calculate_file_hash(backup_file)
                is_valid = actual_hash == expected_hash
                return {
                    "filename": filename,
                    "valid": is_valid,
                    "expected_hash": expected_hash,
                    "actual_hash": actual_hash
                }
            else:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Хеш не найден в метаданных")
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Метаданные backup'а не найдены")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying backup: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось проверить целостность backup'а")