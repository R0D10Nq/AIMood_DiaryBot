#!/usr/bin/env python3
"""
Запуск Telegram Bot
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавляем путь к модулям
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(backend_dir)
sys.path.append(backend_dir)

# Устанавливаем путь к .env файлу
os.chdir(project_dir)

from app.bot.bot import mood_bot


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log', encoding='utf-8')
        ]
    )


async def main():
    """Главная функция запуска бота"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Запускаю AI Mood Diary Telegram Bot...")
    
    try:
        # Инициализируем базу данных
        from app.core.database import create_tables
        logger.info("📚 Инициализирую базу данных...")
        create_tables()
        logger.info("✅ База данных инициализирована")
        
        # Настраиваем приложение
        app = mood_bot.setup_application()
        if not app:
            logger.error("❌ Не удалось настроить приложение бота")
            return
        
        # Запускаем бота
        await mood_bot.run_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал завершения")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        logger.error(f"Трассировка: {traceback.format_exc()}")
    finally:
        logger.info("🔚 Бот завершил работу")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")