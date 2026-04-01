# Telegram Alert Bot for MentorHub
# Бот для отправки уведомлений в Telegram

import asyncio
import logging
from typing import Optional
from aiogram import Bot
from aiogram.types import ParseMode

from ..config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramAlerter:
    """Отправка алертов в Telegram"""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID
        self.bot: Optional[Bot] = None

        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured. Alerts disabled.")
            return

        self.bot = Bot(token=self.bot_token)

    async def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Отправить сообщение в Telegram"""
        if not self.bot:
            logger.warning("Telegram bot not initialized. Skipping alert.")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode(parse_mode),
            )
            logger.info(f"Telegram alert sent: {message[:100]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

    async def send_alert(
        self,
        title: str,
        description: str,
        severity: str = "warning",
        url: Optional[str] = None,
    ) -> bool:
        """Отправить алерт с форматированием"""
        emoji = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(severity, "🔔")

        message = f"{emoji} *{title}*\n\n{description}"

        if url:
            message += f"\n\n🔗 [View Details]({url})"

        return await self.send_message(message)

    async def send_deploy_notification(
        self, status: str, commit_message: str, author: str, commit_url: str
    ) -> bool:
        """Уведомление о деплое"""
        emoji = "✅" if status == "success" else "❌"
        title = f"{emoji} Production Deploy {'Successful' if status == 'success' else 'Failed'}"

        description = f"*Commit:* {commit_message}\n*Author:* {author}"

        return await self.send_alert(title, description, "info", commit_url)

    async def send_error_alert(
        self, error_type: str, error_message: str, traceback_url: Optional[str] = None
    ) -> bool:
        """Уведомление об ошибке"""
        title = f"🔴 {error_type}"
        description = f"```\n{error_message[:500]}\n```"  # Обрезаем до 500 символов

        return await self.send_alert(title, description, "critical", traceback_url)

    async def send_monitoring_alert(
        self, metric_name: str, current_value: str, threshold: str
    ) -> bool:
        """Уведомление от системы мониторинга"""
        title = f"⚠️ Monitoring Alert: {metric_name}"
        description = f"*Current:* {current_value}\n*Threshold:* {threshold}"

        return await self.send_alert(title, description, "warning")

    async def close(self):
        """Закрытие соединения с Telegram"""
        if self.bot:
            await self.bot.session.close()


# Пример использования
async def main():
    alerter = TelegramAlerter()

    # Тестовое сообщение
    await alerter.send_message("👋 Telegram bot initialized!")

    # Алерт о деплое
    await alerter.send_deploy_notification(
        status="success",
        commit_message="fix: critical bug fix",
        author="developer",
        commit_url="https://github.com/org/repo/commit/abc123",
    )

    # Алерт об ошибке
    await alerter.send_error_alert(
        error_type="Database Connection Error",
        error_message="Failed to connect to PostgreSQL after 3 retries",
        traceback_url="https://sentry.io/...",
    )

    # Мониторинг алерт
    await alerter.send_monitoring_alert(
        metric_name="CPU Usage", current_value="95%", threshold="80%"
    )

    await alerter.close()


if __name__ == "__main__":
    asyncio.run(main())
