# numpyp/telegram_handler.py

import telegram
import asyncio


class _TelegramHandler:
    def __init__(self, token: str, chat_id: str):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id
        self.last_message_id = None

    def _run_coroutine(self, coro):
        """
        Умный обработчик, который правильно работает в любой среде.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Если мы в среде с работающим циклом (Jupyter),
            # мы добавляем задачу в этот цикл из другого потока и ждем результат.
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result()
        else:
            # Если мы в обычном скрипте, где цикл не запущен,
            # мы запускаем его сами до выполнения нашей задачи.
            return loop.run_until_complete(coro)

    def send_message(self, text: str):
        """Отправляет сообщение и сохраняет его ID."""
        self._run_coroutine(self._async_send_message(text))

    async def _async_send_message(self, text: str):
        """Асинхронная часть для отправки сообщения."""
        try:
            message = await self.bot.send_message(chat_id=self.chat_id, text=text)
            self.last_message_id = message.message_id
            print(f"✅ Сообщение отправлено. ID для ответа: {self.last_message_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            self.last_message_id = None

    def check_for_reply(self) -> str | None:
        """Проверяет наличие ответа."""
        return self._run_coroutine(self._async_check_for_reply())

    async def _async_check_for_reply(self) -> str | None:
        """Асинхронная часть для проверки ответа."""
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