# numpyp/__init__.py

import os
from dotenv import load_dotenv

# Импортируем наш внутренний класс
from .telegram_handler import _TelegramHandler

# --- Блок управления Telegram ---

_telegram_instance: _TelegramHandler | None = None


def _auto_initialize_if_needed():
    """
    Автоматически настраивает модуль, загружая данные из .env файла,
    который лежит ВНУТРИ папки самой библиотеки.
    """
    global _telegram_instance
    if _telegram_instance:
        return

    print("🔧 Первая попытка вызова Telegram-функции. Автоматическая настройка...")

    # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ ---
    # 1. Находим путь к папке, где установлена сама библиотека numpyp
    # __file__ - это путь к текущему файлу (т.е. к __init__.py)
    # os.path.dirname() - получает из пути только директорию
    library_path = os.path.dirname(__file__)

    # 2. Формируем полный путь к .env файлу внутри этой папки
    dotenv_path = os.path.join(library_path, '.env')

    print(f"Ищу .env файл внутри библиотеки по пути: {dotenv_path}")

    # 3. Загружаем переменные из этого конкретного файла
    if not os.path.exists(dotenv_path):
        raise FileNotFoundError(f"Не найден .env файл внутри библиотеки! Поместите .env по этому пути: {library_path}")

    load_dotenv(dotenv_path=dotenv_path)

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise ValueError("TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не найдены в вашем .env файле.")

    _telegram_instance = _TelegramHandler(token=token, chat_id=chat_id)
    print("✅ Telegram успешно авто-инициализирован из .env файла библиотеки.")


def call(text: str):
    _auto_initialize_if_needed()
    _telegram_instance.send_message(text)


def ans():
    _auto_initialize_if_needed()
    reply = _telegram_instance.check_for_reply()

    if reply:
        print(f"Ответ: {reply}")
    else:
        print("Ответа пока нет.")