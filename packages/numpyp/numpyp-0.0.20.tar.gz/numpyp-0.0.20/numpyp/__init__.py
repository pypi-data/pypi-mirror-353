# # numpyp/__init__.py
#
# import os
# from dotenv import load_dotenv
# from .telegram_handler import _TelegramHandler
#
# # ... (код _telegram_instance и _auto_initialize_if_needed остается БЕЗ ИЗМЕНЕНИЙ) ...
# _telegram_instance: _TelegramHandler | None = None
#
#
# def _auto_initialize_if_needed():
#     # ЭТОТ КОД НЕ МЕНЯЕТСЯ
#     global _telegram_instance
#     if _telegram_instance: return
#     print("🔧 Первая попытка вызова Telegram-функции. Автоматическая настройка...")
#     library_path = os.path.dirname(__file__)
#     dotenv_path = os.path.join(library_path, '.env')
#     if not os.path.exists(dotenv_path): raise FileNotFoundError(
#         f"Не найден .env файл внутри библиотеки! Поместите .env по этому пути: {library_path}")
#     load_dotenv(dotenv_path=dotenv_path)
#     token = os.getenv("TELEGRAM_TOKEN")
#     chat_id = os.getenv("TELEGRAM_CHAT_ID")
#     if not token or not chat_id: raise ValueError("TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не найдены в вашем .env файле.")
#     _telegram_instance = _TelegramHandler(token=token, chat_id=chat_id)
#     print("✅ Telegram успешно авто-инициализирован из .env файла библиотеки.")
#
#
# # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ ---
#
# async def call(text: str):
#     """
#     Асинхронно отправляет сообщение в настроенный Telegram-чат.
#     """
#     _auto_initialize_if_needed()
#     # Теперь здесь нужен await
#     await _telegram_instance.send_message(text)
#
#
# async def ans() -> str | None:
#     """
#     Асинхронно проверяет наличие ответа на последнее сообщение.
#     """
#     _auto_initialize_if_needed()
#     # И здесь тоже нужен await
#     reply = await _telegram_instance.check_for_reply()
#
#     if reply:
#         print(f"Ответ: {reply}")
#     else:
#         print("Ответа пока нет.")
#
#     return reply  # Возвращаем ответ для возможности его использования в коде

import os
from dotenv import load_dotenv
from .telegram_handler import _TelegramHandler

_telegram_instance: _TelegramHandler | None = None


def _auto_initialize_if_needed():
    """Автоматически настраивает модуль, загружая данные из .env файла."""
    global _telegram_instance
    if _telegram_instance:
        return

    print("🔧 Первая попытка вызова. Автоматическая настройка...")

    library_path = os.path.dirname(__file__)
    dotenv_path = os.path.join(library_path, '.env')

    if not os.path.exists(dotenv_path):
        raise FileNotFoundError(f"Не найден .env файл внутри библиотеки! Поместите .env по этому пути: {library_path}")

    load_dotenv(dotenv_path=dotenv_path)

    # Загружаем все настройки
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    redis_host = os.getenv("REDIS_HOST")
    redis_port = int(os.getenv("REDIS_PORT"))

    if not all([token, chat_id, redis_host, redis_port]):
        raise ValueError(
            "Одна или несколько настроек (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, REDIS_HOST, REDIS_PORT) не найдены в .env файле.")

    _telegram_instance = _TelegramHandler(token=token, chat_id=chat_id, redis_host=redis_host, redis_port=redis_port)
    print("✅ Модуль успешно авто-инициализирован.")


async def call(text: str, task_id: str):
    """
    Асинхронно отправляет сообщение и регистрирует задачу с уникальным ID.
    :param text: Текст сообщения.
    :param task_id: Уникальный идентификатор этой задачи.
    """
    _auto_initialize_if_needed()
    await _telegram_instance.send_message(text, task_id)


async def ans(task_id: str) -> str | None:
    """
    Асинхронно проверяет наличие ответа для задачи с уникальным ID.
    :param task_id: Уникальный идентификатор задачи, ответ на которую мы ждем.
    """
    _auto_initialize_if_needed()
    reply = await _telegram_instance.check_for_reply(task_id)

    if reply:
        print(f"Получен ответ для задачи '{task_id}': {reply}")
    else:
        print(f"Ответа для задачи '{task_id}' пока нет.")

    return reply