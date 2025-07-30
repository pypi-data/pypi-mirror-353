# # # #
# # # # import telegram
# # # # import redis
# # # #
# # # #
# # # # class _TelegramHandler:
# # # #     """
# # # #     Внутренний класс-обработчик.
# # # #     Управляет взаимодействием с Telegram API и хранилищем состояний Redis.
# # # #     """
# # # #
# # # #     def __init__(self, token: str, chat_id: str, redis_host: str, redis_port: int):
# # # #         self.bot = telegram.Bot(token=token)
# # # #         self.chat_id = chat_id
# # # #         # Подключаемся к Redis. decode_responses=True чтобы получать строки, а не байты.
# # # #         try:
# # # #             self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
# # # #             # Проверяем подключение, чтобы сразу выявить проблему, если Redis недоступен
# # # #             self.redis_client.ping()
# # # #             print("✅ Подключение к Redis успешно.")
# # # #         except redis.exceptions.ConnectionError as e:
# # # #             print(f"❌ Не удалось подключиться к Redis: {e}")
# # # #             raise ConnectionError("Проверьте, что Redis запущен и доступен по указанному хосту и порту.") from e
# # # #
# # # #     async def send_message(self, text: str, task_id: str):
# # # #         """Асинхронно отправляет сообщение и регистрирует задачу в Redis."""
# # # #         try:
# # # #             message = await self.bot.send_message(chat_id=self.chat_id, text=text)
# # # #             # Сохраняем ID сообщения в Redis с ключом задачи.
# # # #             # Ставим срок жизни ключа - 24 часа (86400 секунд), чтобы не засорять базу старыми задачами.
# # # #             self.redis_client.set(f"task:{task_id}", message.message_id, ex=86400)
# # # #             print(f"✅ Сообщение для задачи '{task_id}' отправлено. ID: {message.message_id}")
# # # #         except Exception as e:
# # # #             print(f"❌ Ошибка отправки сообщения для задачи '{task_id}': {e}")
# # # #
# # # #     async def check_for_reply(self, task_id: str) -> str | None:
# # # #         """Асинхронно проверяет ответ для конкретной задачи."""
# # # #         # Получаем ID сообщения из Redis по ключу задачи
# # # #         message_id_to_check_str = self.redis_client.get(f"task:{task_id}")
# # # #
# # # #         if not message_id_to_check_str:
# # # #             # Задача не найдена - возможно, уже выполнена или время жизни истекло.
# # # #             return None
# # # #
# # # #         message_id_to_check = int(message_id_to_check_str)
# # # #
# # # #         try:
# # # #             updates = await self.bot.get_updates(timeout=1)
# # # #             for update in reversed(updates):
# # # #                 msg = update.message
# # # #                 # Ищем ответ на наше конкретное сообщение
# # # #                 if (msg and msg.reply_to_message and
# # # #                         msg.reply_to_message.message_id == message_id_to_check):
# # # #                     print(f"✅ Найден ответ для задачи '{task_id}'.")
# # # #                     # Задача выполнена, удаляем ее из Redis, чтобы не проверять снова.
# # # #                     self.redis_client.delete(f"task:{task_id}")
# # # #                     return msg.text
# # # #             return None  # Ответа пока нет
# # # #         except Exception as e:
# # # #             print(f"❌ Ошибка получения ответа для задачи '{task_id}': {e}")
# # # #             return None
# # #
# # # # numpyp/telegram_handler.py
# # #
# # # import telegram
# # # import redis
# # #
# # #
# # # class _TelegramHandler:
# # #     def __init__(self, token: str, chat_id: str, redis_host: str, redis_port: int):
# # #         self.bot = telegram.Bot(token=token)
# # #         self.chat_id = chat_id
# # #         try:
# # #             self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
# # #             self.redis_client.ping()
# # #             print("✅ Подключение к Redis успешно.")
# # #         except redis.exceptions.ConnectionError as e:
# # #             print(f"❌ Не удалось подключиться к Redis: {e}")
# # #             raise ConnectionError("Проверьте, что Redis запущен и доступен по указанному хосту и порту.") from e
# # #
# # #     async def send_message(self, text: str, task_id: str):
# # #         """Асинхронно отправляет форматированное сообщение и регистрирует задачу."""
# # #         # --- ИЗМЕНЕНИЕ 1: ФОРМАТИРУЕМ ТЕКСТ ---
# # #         formatted_text = f"--{task_id}--\n\n{text}"
# # #
# # #         try:
# # #             message = await self.bot.send_message(chat_id=self.chat_id, text=formatted_text)
# # #             # Ключ для основного сообщения задачи. Срок жизни 24 часа.
# # #             task_key = f"task:{task_id}"
# # #             self.redis_client.set(task_key, message.message_id, ex=86400)
# # #
# # #             # Также установим срок жизни для набора обработанных ответов, чтобы он не висел вечно
# # #             processed_replies_key = f"task:{task_id}:processed_replies"
# # #             self.redis_client.expire(processed_replies_key, 86400)
# # #
# # #             print(f"✅ Сообщение для задачи '{task_id}' отправлено. ID: {message.message_id}")
# # #         except Exception as e:
# # #             print(f"❌ Ошибка отправки сообщения для задачи '{task_id}': {e}")
# # #
# # #     async def check_for_reply(self, task_id: str) -> str | None:
# # #         """Асинхронно проверяет НОВЫЙ, еще не обработанный ответ для задачи."""
# # #         task_key = f"task:{task_id}"
# # #         processed_replies_key = f"task:{task_id}:processed_replies"
# # #
# # #         message_id_to_check_str = self.redis_client.get(task_key)
# # #         if not message_id_to_check_str:
# # #             return None  # Задачи не существует
# # #
# # #         message_id_to_check = int(message_id_to_check_str)
# # #
# # #         try:
# # #             updates = await self.bot.get_updates(timeout=1)
# # #             # --- ИЗМЕНЕНИЕ 2: ЛОГИКА МНОЖЕСТВЕННЫХ ОТВЕТОВ ---
# # #             processed_reply_ids = self.redis_client.smembers(processed_replies_key)
# # #
# # #             for update in reversed(updates):
# # #                 msg = update.message
# # #                 if (msg and msg.reply_to_message and
# # #                         msg.reply_to_message.message_id == message_id_to_check):
# # #
# # #                     # Проверяем, видели ли мы уже этот ответ
# # #                     if str(msg.message_id) not in processed_reply_ids:
# # #                         print(f"✅ Найден НОВЫЙ ответ для задачи '{task_id}'. ID ответа: {msg.message_id}")
# # #                         # Добавляем ID этого ответа в набор "обработанных"
# # #                         self.redis_client.sadd(processed_replies_key, msg.message_id)
# # #                         return msg.text  # Возвращаем текст нового ответа
# # #
# # #             return None  # Новых неотвеченных сообщений нет
# # #         except Exception as e:
# # #             print(f"❌ Ошибка получения ответа для задачи '{task_id}': {e}")
# # #             return None
# #
# # import telegram
# # import redis
# #
# #
# # class _TelegramHandler:
# #     """
# #     Внутренний класс-обработчик.
# #     Управляет взаимодействием с Telegram API и хранилищем состояний Redis.
# #     """
# #
# #     def __init__(self, token: str, chat_id: str, redis_host: str, redis_port: int):
# #         self.bot = telegram.Bot(token=token)
# #         self.chat_id = chat_id
# #         try:
# #             self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
# #             self.redis_client.ping()
# #             print("✅ Подключение к Redis успешно.")
# #         except redis.exceptions.ConnectionError as e:
# #             print(f"❌ Не удалось подключиться к Redis: {e}")
# #             raise ConnectionError("Проверьте, что Redis запущен и доступен по указанному хосту и порту.") from e
# #
# #     async def send_message(self, text: str, task_id: str):
# #         """Асинхронно отправляет форматированное сообщение и регистрирует задачу."""
# #         formatted_text = f"--{task_id}--\n\n{text}"
# #
# #         try:
# #             message = await self.bot.send_message(chat_id=self.chat_id, text=formatted_text)
# #             task_key = f"task:{task_id}"
# #             processed_replies_key = f"task:{task_id}:processed_replies"
# #
# #             # Сохраняем ID основного сообщения. Срок жизни 24 часа.
# #             self.redis_client.set(task_key, message.message_id, ex=86400)
# #             # Устанавливаем срок жизни для набора ответов, чтобы он тоже удалился.
# #             self.redis_client.expire(processed_replies_key, 86400)
# #
# #             print(f"✅ Сообщение для задачи '{task_id}' отправлено. ID: {message.message_id}")
# #         except Exception as e:
# #             print(f"❌ Ошибка отправки сообщения для задачи '{task_id}': {e}")
# #
# #     async def check_for_reply(self, task_id: str) -> dict | None:
# #         """Асинхронно проверяет НОВЫЙ, еще не обработанный ответ для задачи."""
# #         task_key = f"task:{task_id}"
# #         processed_replies_key = f"task:{task_id}:processed_replies"
# #
# #         message_id_to_check_str = self.redis_client.get(task_key)
# #         if not message_id_to_check_str:
# #             return None  # Задачи не существует или ее время жизни истекло
# #
# #         message_id_to_check = int(message_id_to_check_str)
# #
# #         try:
# #             updates = await self.bot.get_updates(timeout=1)
# #             processed_reply_ids = self.redis_client.smembers(processed_replies_key)
# #
# #             for update in reversed(updates):
# #                 msg = update.message
# #                 if (msg and msg.reply_to_message and
# #                         msg.reply_to_message.message_id == message_id_to_check):
# #
# #                     if str(msg.message_id) not in processed_reply_ids:
# #                         print(f"✅ Найден НОВЫЙ ответ для задачи '{task_id}'. ID ответа: {msg.message_id}")
# #                         self.redis_client.sadd(processed_replies_key, msg.message_id)
# #
# #                         # Собираем словарь с информацией об авторе ответа и текстом
# #                         return {
# #                             "username": msg.from_user.username or "N/A",
# #                             "first_name": msg.from_user.first_name,
# #                             "text": msg.text,
# #                             "user_id": msg.from_user.id
# #                         }
# #
# #             return None  # Новых необработанных ответов нет
# #         except Exception as e:
# #             print(f"❌ Ошибка получения ответа для задачи '{task_id}': {e}")
# #             return None
#
# # numpyp/telegram_handler.py
#
# import telegram
# import redis
# import time
#
#
# class _TelegramHandler:
#     def __init__(self, token: str, chat_id: str, redis_host: str, redis_port: int):
#         self.bot = telegram.Bot(token=token)
#         self.chat_id = chat_id
#
#         # Вместо прямого подключения, вызываем наш новый "умный" метод
#         self.redis_client = self._connect_to_redis_with_scan(host=redis_host, base_port=redis_port)
#
#     def _connect_to_redis_with_scan(self, host: str, base_port: int, scan_range: int = 10):
#         """
#         Пытается подключиться к Redis, сканируя порты по очереди.
#         ВНИМАНИЕ: Это не является стандартной практикой.
#         """
#         for i in range(scan_range):
#             port_to_try = base_port + i
#             print(f"Пытаюсь подключиться к Redis по адресу {host}:{port_to_try}...")
#             try:
#                 # Создаем временный клиент для проверки
#                 r = redis.Redis(host=host, port=port_to_try, decode_responses=True)
#                 # Команда ping() - лучший способ проверить живое соединение.
#                 # Она либо вернет True, либо вызовет исключение.
#                 r.ping()
#
#                 # Если мы дошли сюда, значит исключения не было и соединение успешно!
#                 print(f"✅ Успешное подключение к Redis на порту {port_to_try}!")
#                 return r  # Возвращаем рабочий клиент
#
#             except redis.exceptions.ConnectionError:
#                 # Если порт не отвечает, просто игнорируем ошибку и переходим к следующему.
#                 print(f"Порт {port_to_try} не отвечает. Пробую следующий...")
#                 time.sleep(0.1)  # Небольшая пауза
#
#         # Если мы прошли весь цикл и не смогли подключиться, вызываем финальную ошибку.
#         raise ConnectionError(
#             f"Не удалось подключиться к Redis ни на одном из портов в диапазоне "
#             f"{base_port}-{base_port + scan_range - 1}. "
#             f"Убедитесь, что Redis-сервер запущен."
#         )
#
#     # --- Остальные методы (send_message, check_for_reply) остаются БЕЗ ИЗМЕНЕНИЙ ---
#
#     async def send_message(self, text: str, task_id: str):
#         # Этот код не меняется
#         formatted_text = f"--{task_id}--\n\n{text}"
#         try:
#             message = await self.bot.send_message(chat_id=self.chat_id, text=formatted_text)
#             task_key = f"task:{task_id}"
#             processed_replies_key = f"task:{task_id}:processed_replies"
#             self.redis_client.set(task_key, message.message_id, ex=86400)
#             self.redis_client.expire(processed_replies_key, 86400)
#             print(f"✅ Сообщение для задачи '{task_id}' отправлено. ID: {message.message_id}")
#         except Exception as e:
#             print(f"❌ Ошибка отправки сообщения для задачи '{task_id}': {e}")
#
#     async def check_for_reply(self, task_id: str) -> dict | None:
#         # И этот код не меняется
#         task_key = f"task:{task_id}"
#         processed_replies_key = f"task:{task_id}:processed_replies"
#         message_id_to_check_str = self.redis_client.get(task_key)
#         if not message_id_to_check_str:
#             return None
#         message_id_to_check = int(message_id_to_check_str)
#         try:
#             updates = await self.bot.get_updates(timeout=1)
#             processed_reply_ids = self.redis_client.smembers(processed_replies_key)
#             for update in reversed(updates):
#                 msg = update.message
#                 if (msg and msg.reply_to_message and
#                         msg.reply_to_message.message_id == message_id_to_check):
#                     if str(msg.message_id) not in processed_reply_ids:
#                         print(f"✅ Найден НОВЫЙ ответ для задачи '{task_id}'. ID ответа: {msg.message_id}")
#                         self.redis_client.sadd(processed_replies_key, msg.message_id)
#                         return {"username": msg.from_user.username or "N/A", "first_name": msg.from_user.first_name,
#                                 "text": msg.text, "user_id": msg.from_user.id}
#             return None
#         except Exception as e:
#             print(f"❌ Ошибка получения ответа для задачи '{task_id}': {e}")
#             return None

# numpyp/telegram_handler.py

import telegram
import redislite  # <-- Импортируем redislite вместо redis
import os


class _TelegramHandler:
    """
    Внутренний класс-обработчик.
    Использует redislite для автономного хранения состояний.
    """

    def __init__(self, token: str, chat_id: str):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id

        # --- НОВАЯ ЛОГИКА ИНИЦИАЛИЗАЦИИ REDIS ---
        # Получаем путь к папке, где лежит сама библиотека
        library_path = os.path.dirname(__file__)
        # Указываем, что файл базы данных будет лежать прямо здесь же
        db_file_path = os.path.join(library_path, 'numpyp_redis.db')

        print(f"Использую файл базы данных Redis: {db_file_path}")

        # Создаем подключение к redislite. Если файла нет, он будет создан.
        # Если есть - будет использоваться существующий.
        self.redis_client = redislite.Redis(db_file_path)
        print("✅ Автономный Redis (redislite) успешно инициализирован.")
        # --- КОНЕЦ НОВОЙ ЛОГИКИ ---

    # --- ВСЕ ОСТАЛЬНЫЕ МЕТОДЫ (send_message, check_for_reply) ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЙ! ---
    # Они используют стандартный API Redis, поэтому будут работать с redislite "из коробки".

    async def send_message(self, text: str, task_id: str):
        formatted_text = f"--{task_id}--\n\n{text}"
        try:
            message = await self.bot.send_message(chat_id=self.chat_id, text=formatted_text)
            task_key = f"task:{task_id}"
            processed_replies_key = f"task:{task_id}:processed_replies"
            self.redis_client.set(task_key, message.message_id, ex=86400)
            self.redis_client.expire(processed_replies_key, 86400)
            print(f"✅ Сообщение для задачи '{task_id}' отправлено. ID: {message.message_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения для задачи '{task_id}': {e}")

    async def check_for_reply(self, task_id: str) -> dict | None:
        task_key = f"task:{task_id}"
        processed_replies_key = f"task:{task_id}:processed_replies"
        message_id_to_check_str = self.redis_client.get(task_key)
        if not message_id_to_check_str:
            return None
        message_id_to_check = int(message_id_to_check_str)
        try:
            updates = await self.bot.get_updates(timeout=1)
            processed_reply_ids = self.redis_client.smembers(processed_replies_key)
            for update in reversed(updates):
                msg = update.message
                if (msg and msg.reply_to_message and
                        msg.reply_to_message.message_id == message_id_to_check):
                    if str(msg.message_id) not in processed_reply_ids:
                        print(f"✅ Найден НОВЫЙ ответ для задачи '{task_id}'. ID ответа: {msg.message_id}")
                        self.redis_client.sadd(processed_replies_key, msg.message_id)
                        return {"username": msg.from_user.username or "N/A", "first_name": msg.from_user.first_name,
                                "text": msg.text, "user_id": msg.from_user.id}
            return None
        except Exception as e:
            print(f"❌ Ошибка получения ответа для задачи '{task_id}': {e}")
            return None