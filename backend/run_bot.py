"""
Запуск Telegram Bot для AI Mood Diary
"""

import asyncio
import logging
import sys
import os

# Добавляем путь к модулям приложения
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.bot.bot import mood_bot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    try:
        # Настраиваем приложение бота
        application = mood_bot.setup_application()
        
        if not application:
            logger.error("❌ Не удалось настроить Telegram Bot")
            return
        
        # Запускаем бота
        await mood_bot.run_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        logger.info("👋 Telegram Bot остановлен")


if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())