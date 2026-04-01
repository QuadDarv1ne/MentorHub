"""
Two-Factor Authentication Service
TOTP (Time-based One-Time Password) implementation
"""

import logging
import secrets
import string
from typing import Optional, Tuple, Dict, Any

import pyotp
import qrcode
from io import BytesIO
import base64

from app.models.user import User

logger = logging.getLogger(__name__)


class TwoFactorService:
    """Сервис для управления двухфакторной аутентификацией"""

    @staticmethod
    def generate_secret() -> str:
        """Генерация TOTP секрета"""
        return pyotp.random_base32()

    @staticmethod
    def get_provisioning_uri(email: str, secret: str, issuer: str = "MentorHub") -> str:
        """Генерация URI для QR кода"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)

    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """Генерация QR кода в Base64"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def generate_backup_codes(count: int = 10, length: int = 8) -> list[str]:
        """Генерация backup кодов"""
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.digits) for _ in range(length))
            codes.append(code)
        return codes

    @staticmethod
    def verify_totp(secret: str, code: str, window: int = 1) -> bool:
        """
        Проверка TOTP кода
        
        Args:
            secret: TOTP секрет пользователя
            code: Код от приложения
            window: Допустимое отклонение по времени (в шагах)
        
        Returns:
            True если код верный
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=window)

    @staticmethod
    def verify_backup_code(backup_codes: Optional[str], code: str) -> bool:
        """Проверка backup кода"""
        if not backup_codes:
            return False
        
        try:
            import json
            codes = json.loads(backup_codes)
            return code in codes
        except (json.JSONDecodeError, TypeError):
            return False

    @staticmethod
    def remove_backup_code(backup_codes: Optional[str], used_code: str) -> Optional[str]:
        """Удалить использованный backup код"""
        if not backup_codes:
            return None
        
        try:
            import json
            codes = json.loads(backup_codes)
            if used_code in codes:
                codes.remove(used_code)
                return json.dumps(codes)
        except (json.JSONDecodeError, TypeError):
            pass
        
        return backup_codes

    def setup_2fa(self, user: User) -> Dict[str, Any]:
        """
        Настройка 2FA для пользователя
        
        Returns:
            Dict с secret, qr_code и provisioning_uri
        """
        if user.two_factor_enabled:
            raise ValueError("2FA уже включена")

        secret = self.generate_secret()
        provisioning_uri = self.get_provisioning_uri(user.email, secret)
        qr_code = self.generate_qr_code(provisioning_uri)

        # Сохраняем секрет (но не включаем 2FA пока)
        user.two_factor_secret = secret

        return {
            "secret": secret,
            "qr_code": qr_code,
            "provisioning_uri": provisioning_uri,
            "backup_codes": []  # Будут сгенерированы при подтверждении
        }

    def enable_2fa(self, user: User, code: str) -> Tuple[bool, list[str]]:
        """
        Включение 2FA после проверки кода
        
        Returns:
            Tuple (success, backup_codes)
        """
        if not user.two_factor_secret:
            raise ValueError("2FA секрет не установлен")

        # Проверяем код
        if not self.verify_totp(user.two_factor_secret, code):
            return False, []

        # Включаем 2FA
        user.two_factor_enabled = True
        
        # Генерируем backup коды
        import json
        backup_codes = self.generate_backup_codes()
        user.two_factor_backup_codes = json.dumps(backup_codes)

        return True, backup_codes

    def disable_2fa(self, user: User, code: Optional[str] = None) -> bool:
        """
        Отключение 2FA
        
        Args:
            user: Пользователь
            code: TOTP код или backup код (для подтверждения)
        
        Returns:
            True если успешно
        """
        if not user.two_factor_enabled:
            return True

        # Если предоставлен код, проверяем его
        if code:
            if self.verify_totp(user.two_factor_secret or "", code):
                pass  # Код верный
            elif self.verify_backup_code(user.two_factor_backup_codes, code):
                # Используем backup код
                user.two_factor_backup_codes = self.remove_backup_code(
                    user.two_factor_backup_codes, code
                )
            else:
                raise ValueError("Неверный код подтверждения")

        # Отключаем 2FA
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.two_factor_backup_codes = None

        return True

    def verify_2fa(self, user: User, code: str) -> bool:
        """
        Проверка 2FA при входе
        
        Returns:
            True если код верный
        """
        if not user.two_factor_enabled or not user.two_factor_secret:
            return True  # 2FA не включена

        # Проверяем TOTP
        if self.verify_totp(user.two_factor_secret, code):
            return True

        # Проверяем backup код
        if self.verify_backup_code(user.two_factor_backup_codes, code):
            # Удаляем использованный код
            user.two_factor_backup_codes = self.remove_backup_code(
                user.two_factor_backup_codes, code
            )
            return True

        return False

    def regenerate_backup_codes(self, user: User) -> list[str]:
        """Перегенерация backup кодов"""
        if not user.two_factor_enabled:
            raise ValueError("2FA не включена")

        import json
        backup_codes = self.generate_backup_codes()
        user.two_factor_backup_codes = json.dumps(backup_codes)
        
        return backup_codes


# Глобальный экземпляр сервиса
two_factor_service = TwoFactorService()
