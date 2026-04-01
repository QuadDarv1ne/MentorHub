"""
Agora Video Service
Генерация токенов для видеозвонков
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Optional


# Agora конфигурация
AGORA_APP_ID = os.getenv("AGORA_APP_ID", "")
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE", "")

try:
    from agora_token_builder import RtcTokenBuilder, RtcTokenBuilderRole
    AGORA_AVAILABLE = True
except ImportError:
    AGORA_AVAILABLE = False


class AgoraService:
    """Сервис для работы с Agora API"""

    def __init__(self):
        self.app_id = AGORA_APP_ID
        self.app_certificate = AGORA_APP_CERTIFICATE
        self.available = AGORA_AVAILABLE and bool(self.app_id) and bool(self.app_certificate)

    def generate_token(
        self,
        channel: str,
        uid: int,
        role: str = "publisher",
        expiration: int = 3600
    ) -> str:
        """
        Генерация токена Agora для подключения к каналу

        Args:
            channel: Имя канала
            uid: ID пользователя
            role: Роль (publisher/subscriber)
            expiration: Время действия в секундах

        Returns:
            Токен доступа или пустая строка при ошибке
        """
        if not self.available:
            return ""

        try:
            current_time = datetime.now(timezone.utc)
            privilege_expired_ts = int((current_time + timedelta(seconds=expiration)).timestamp())

            rtc_role = RtcTokenBuilderRole.PUBLISHER if role == "publisher" else RtcTokenBuilderRole.SUBSCRIBER

            token = RtcTokenBuilder.build_token_with_uid(
                self.app_id,
                self.app_certificate,
                channel,
                uid,
                rtc_role,
                privilege_expired_ts
            )
            return token
        except Exception:
            return ""

    def get_app_id(self) -> str:
        """Получить App ID для frontend"""
        return self.app_id

    def is_available(self) -> bool:
        """Проверить доступность сервиса"""
        return self.available


# Глобальный экземпляр сервиса
agora_service = AgoraService()
