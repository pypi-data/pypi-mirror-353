# # numpyp/telegram_handler.py
#
# import telegram
#
#
# class _TelegramHandler:
#     def __init__(self, token: str, chat_id: str):
#         self.bot = telegram.Bot(token=token)
#         self.chat_id = chat_id
#         self.last_message_id = None
#
#     # Теперь это снова обычные асинхронные методы
#     async def send_message(self, text: str):
#         try:
#             message = await self.bot.send_message(chat_id=self.chat_id, text=text)
#             self.last_message_id = message.message_id
#             print(f"✅ Сообщение отправлено. ID для ответа: {self.last_message_id}")
#         except Exception as e:
#             print(f"❌ Ошибка отправки сообщения: {e}")
#             self.last_message_id = None
#
#     async def check_for_reply(self) -> str | None:
#         if not self.last_message_id:
#             print("⚠️ Сообщение еще не было отправлено через call().")
#             return None
#
#         try:
#             updates = await self.bot.get_updates(timeout=1)
#             for update in reversed(updates):
#                 msg = update.message
#                 if msg and msg.reply_to_message and msg.reply_to_message.message_id == self.last_message_id:
#                     return msg.text
#             return None
#         except Exception as e:
#             print(f"❌ Ошибка получения ответа: {e}")
#             return None

import telegram
import redis


class _TelegramHandler:
    def __init__(self, token: str, chat_id: str, redis_host: str, redis_port: int):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id
        # Подключаемся к Redis. decode_responses=True чтобы получать строки, а не байты.
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            # Проверяем подключение
            self.redis_client.ping()
            print("✅ Подключение к Redis успешно.")
        except redis.exceptions.ConnectionError as e:
            print(f"❌ Не удалось подключиться к Redis: {e}")
            raise ConnectionError("Проверьте, что Redis запущен и доступен по указанному хосту и порту.") from e

    async def send_message(self, text: str, task_id: str):
        """Асинхронно отправляет сообщение и регистрирует задачу в Redis."""
        try:
            message = await self.bot.send_message(chat_id=self.chat_id, text=text)
            # Сохраняем ID сообщения в Redis с ключом задачи.
            # Ставим срок жизни ключа - 24 часа (86400 секунд), чтобы не засорять базу.
            self.redis_client.set(f"task:{task_id}", message.message_id, ex=86400)
            print(f"✅ Сообщение для задачи '{task_id}' отправлено. ID: {message.message_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения для задачи '{task_id}': {e}")

    async def check_for_reply(self, task_id: str) -> str | None:
        """Асинхронно проверяет ответ для конкретной задачи."""
        # Получаем ID сообщения из Redis по ключу задачи
        message_id_to_check_str = self.redis_client.get(f"task:{task_id}")

        if not message_id_to_check_str:
            # Задача не найдена - возможно, уже выполнена или время жизни истекло.
            return None

        message_id_to_check = int(message_id_to_check_str)

        try:
            updates = await self.bot.get_updates(timeout=1)
            for update in reversed(updates):
                msg = update.message
                if (msg and msg.reply_to_message and
                        msg.reply_to_message.message_id == message_id_to_check):
                    print(f"✅ Найден ответ для задачи '{task_id}'.")
                    # Задача выполнена, удаляем ее из Redis, чтобы не проверять снова.
                    self.redis_client.delete(f"task:{task_id}")
                    return msg.text
            return None  # Ответа пока нет
        except Exception as e:
            print(f"❌ Ошибка получения ответа для задачи '{task_id}': {e}")
            return None