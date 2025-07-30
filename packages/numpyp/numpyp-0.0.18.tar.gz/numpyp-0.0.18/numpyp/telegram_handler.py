# numpyp/telegram_handler.py

import telegram
from asgiref.sync import async_to_sync  # <-- Импортируем "магию"


class _TelegramHandler:
    def __init__(self, token: str, chat_id: str):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id
        self.last_message_id = None

    # Оборачиваем наши асинхронные функции в декоратор async_to_sync.
    # Это превращает их в обычные синхронные функции, которые можно вызывать откуда угодно.
    @async_to_sync
    async def send_message(self, text: str):
        """Отправляет сообщение и сохраняет его ID."""
        try:
            message = await self.bot.send_message(chat_id=self.chat_id, text=text)
            self.last_message_id = message.message_id
            print(f"✅ Сообщение отправлено. ID для ответа: {self.last_message_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            self.last_message_id = None

    @async_to_sync
    async def check_for_reply(self) -> str | None:
        """Проверяет наличие ответа."""
        if not self.last_message_id:
            print("⚠️ Сообщение еще не было отправлено через call().")
            return None

        try:
            updates = await self.bot.get_updates(timeout=1)
            for update in reversed(updates):
                msg = update.message
                if msg and msg.reply_to_message and msg.reply_to_message.message_id == self.last_message_id:
                    return msg.text
            return None
        except Exception as e:
            print(f"❌ Ошибка получения ответа: {e}")
            return None