# numpyp/__init__.py

import os
from dotenv import load_dotenv

# Импортируем наш внутренний класс
from .telegram_handler import _TelegramHandler

# --- Блок управления Telegram ---

# Глобальная переменная модуля, которая хранит настроенный экземпляр.
# Изначально она пустая.
_telegram_instance: _TelegramHandler | None = None


def _auto_initialize_if_needed():
    """
    Внутренняя "магическая" функция.
    Проверяет, был ли уже настроен модуль. Если нет - настраивает его,
    загружая данные из .env файла.
    """
    global _telegram_instance
    # Если экземпляр уже существует, ничего не делаем.
    if _telegram_instance:
        return

    print("🔧 Первая попытка вызова Telegram-функции. Автоматическая настройка...")

    # Ищем и загружаем .env файл из папки, где запущен главный скрипт
    # find_dotenv() найдет .env поднимаясь по папкам вверх
    from dotenv import find_dotenv
    dotenv_path = find_dotenv()

    if not dotenv_path:
        raise FileNotFoundError(
            "Не найден .env файл! Создайте .env рядом с вашим скриптом и поместите в него TELEGRAM_TOKEN и TELEGRAM_CHAT_ID.")

    load_dotenv(dotenv_path)

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise ValueError("TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не найдены в .env файле.")

    # Создаем и сохраняем экземпляр обработчика
    _telegram_instance = _TelegramHandler(token=token, chat_id=chat_id)
    print("✅ Telegram успешно авто-инициализирован из .env файла.")


def call(text: str):
    """
    Отправляет сообщение в настроенный по .env файлу Telegram-чат.
    """
    # Эта функция сама вызовет настройку при первом запуске
    _auto_initialize_if_needed()
    _telegram_instance.send_message(text)


def ans():
    """
    Проверяет наличие ответа на последнее сообщение и выводит его в консоль.
    """
    # И эта функция сама вызовет настройку, если call() не вызывался первым
    _auto_initialize_if_needed()

    reply = _telegram_instance.check_for_reply()

    if reply:
        print(f"Ответ: {reply}")
    else:
        print("Ответа пока нет.")