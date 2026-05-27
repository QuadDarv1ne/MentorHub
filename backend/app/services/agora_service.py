"""
Agora Video Service
Сервис для работы с Agora SDK (видеозвонки)
"""

import logging
import time
from typing import Any, Dict, Optional

from agora_token_builder import RtcTokenBuilder

from app.config import settings

logger = logging.getLogger(__name__)


class AgoraService:
    """
    Сервис для генерации токенов Agora и управления видеозвонками
    """

    def __init__(self):
        self.app_id = settings.AGORA_APP_ID
        self.app_certificate = settings.AGORA_APP_CERTIFICATE
        self.token_expiration_seconds = 3600  # 1 hour
        self.privilege_expiration_seconds = 3600  # 1 hour

    def generate_rtc_token(
        self,
        channel_name: str,
        uid: int = 0,
        role: int = 1,  # 1 = Publisher, 2 = Subscriber
        expiration_seconds: Optional[int] = None
    ) -> str:
        """
        Генерация RTC токена для видеозвонка

        Args:
            channel_name: Имя канала (обычно call_id)
            uid: User ID (0 для автоматического назначения)
            role: Роль пользователя (1 = Publisher, 2 = Subscriber)
            expiration_seconds: Время жизни токена в секундах

        Returns:
            str: Agora RTC токен
        """
        if not self.app_id or not self.app_certificate:
            logger.error("Agora credentials not configured")
            raise ValueError("Agora credentials not configured")

        expiration = expiration_seconds or self.token_expiration_seconds
        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + expiration

        try:
            token = RtcTokenBuilder.buildTokenWithUid(
                self.app_id,
                self.app_certificate,
                channel_name,
                uid,
                role,
                privilege_expired_ts
            )

            logger.info(f"Generated Agora token for channel: {channel_name}, uid: {uid}")
            return token

        except Exception as e:
            logger.error(f"Failed to generate Agora token: {e}")
            raise ValueError(f"Failed to generate Agora token: {str(e)}")

    def generate_token_for_call(
        self,
        call_id: int,
        user_id: int,
        is_host: bool = False
    ) -> Dict[str, Any]:
        """
        Генерация токена для конкретного видеозвонка

        Args:
            call_id: ID видеозвонка
            user_id: ID пользователя
            is_host: Является ли пользователь хостом (создателем звонка)

        Returns:
            Dict с токеном и метаданными
        """
        channel_name = f"call_{call_id}"
        role = 1  # Publisher (может публиковать видео/аудио)

        token = self.generate_rtc_token(
            channel_name=channel_name,
            uid=user_id,
            role=role
        )

        return {
            "token": token,
            "channel_name": channel_name,
            "uid": user_id,
            "app_id": self.app_id,
            "expires_at": int(time.time()) + self.token_expiration_seconds,
            "is_host": is_host
        }

    def validate_channel_name(self, channel_name: str) -> bool:
        """
        Валидация имени канала

        Args:
            channel_name: Имя канала

        Returns:
            bool: True если валидно
        """
        # Agora channel name requirements:
        # - ASCII characters only
        # - Max 64 characters
        # - Can contain: a-z, A-Z, 0-9, !, #, $, %, &, (, ), +, -, :, ;, <, =, ., >, ?, @, [, ], ^, _, {, }, |, ~, ,

        if not channel_name:
            return False

        if len(channel_name) > 64:
            return False

        # Check ASCII
        try:
            channel_name.encode('ascii')
        except UnicodeEncodeError:
            return False

        return True

    def get_recording_config(self, call_id: int) -> Dict[str, Any]:
        """
        Получить конфигурацию для записи видеозвонка

        Args:
            call_id: ID видеозвонка

        Returns:
            Dict с конфигурацией записи
        """
        return {
            "channel_name": f"call_{call_id}",
            "recording_mode": "composite",  # composite or individual
            "max_idle_time": 30,  # seconds
            "stream_types": 2,  # 0=audio, 1=video, 2=both
            "video_stream_type": 0,  # 0=high, 1=low
            "transcoding_config": {
                "width": 1280,
                "height": 720,
                "fps": 30,
                "bitrate": 2000,  # kbps
                "max_resolution_uid": None,
                "layout": "floating"  # floating, best_fit, vertical
            }
        }


# Singleton instance
agora_service = AgoraService()
