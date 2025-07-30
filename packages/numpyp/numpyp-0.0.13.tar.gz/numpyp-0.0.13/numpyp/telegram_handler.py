# numpyp/telegram_handler.py

import telegram
import asyncio  # <-- Импортируем asyncio


class _TelegramHandler:
    """
    Внутренний класс-обработчик.
    Корректно работает с асинхронной библиотекой python-telegram-bot.
    """

    def __init__(self, token: str, chat_id: str):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id
        self.last_message_id = None

    # --- КЛЮЧЕВЫЕ ИЗМЕНЕНИЯ ЗДЕСЬ ---

    def send_message(self, text: str):
        """Отправляет сообщение и сохраняет его ID, используя asyncio."""
        # Мы запускаем асинхронную операцию из нашего синхронного метода
        asyncio.run(self._async_send_message(text))

    async def _async_send_message(self, text: str):
        """Асинхронная часть для отправки сообщения."""
        try:
            # Теперь мы используем 'await', чтобы дождаться выполнения "обещания"
            message = await self.bot.send_message(chat_id=self.chat_id, text=text)
            self.last_message_id = message.message_id
            print(f"✅ Сообщение отправлено. ID для ответа: {self.last_message_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            self.last_message_id = None

    def check_for_reply(self) -> str | None:
        """Проверяет наличие ответа, используя asyncio."""
        # Точно так же запускаем асинхронную проверку
        return asyncio.run(self._async_check_for_reply())

    async def _async_check_for_reply(self) -> str | None:
        """Асинхронная часть для проверки ответа."""
        if not self.last_message_id:
            print("⚠️ Сообщение еще не было отправлено через call().")
            return None

        try:
            # И здесь тоже используем 'await'
            updates = await self.bot.get_updates(timeout=1)
            for update in reversed(updates):
                msg = update.message
                if msg and msg.reply_to_message and msg.reply_to_message.message_id == self.last_message_id:
                    return msg.text
            return None
        except Exception as e:
            print(f"❌ Ошибка получения ответа: {e}")
            return None