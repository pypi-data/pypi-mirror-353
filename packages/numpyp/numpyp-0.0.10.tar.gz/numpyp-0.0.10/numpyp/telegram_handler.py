# numpyp/telegram_handler.py

import telegram


class _TelegramHandler:
    """
    Внутренний класс-обработчик. Пользователи не должны его видеть.
    Хранит состояние (токен, ID чата, ID последнего сообщения).
    """

    def __init__(self, token: str, chat_id: str):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id
        self.last_message_id = None

    def send_message(self, text: str):
        """Просто отправляет сообщение и сохраняет его ID."""
        try:
            message = self.bot.send_message(chat_id=self.chat_id, text=text)
            self.last_message_id = message.message_id
            print(f"✅ Сообщение отправлено. ID для ответа: {self.last_message_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            self.last_message_id = None

    def check_for_reply(self) -> str | None:
        """Однакратная проверка наличия ответа."""
        if not self.last_message_id:
            print("⚠️ Сообщение еще не было отправлено через call().")
            return None

        try:
            updates = self.bot.get_updates(timeout=1)
            for update in reversed(updates):
                msg = update.message
                if msg and msg.reply_to_message and msg.reply_to_message.message_id == self.last_message_id:
                    return msg.text
            return None  # Ответа нет
        except Exception as e:
            print(f"❌ Ошибка получения ответа: {e}")
            return None