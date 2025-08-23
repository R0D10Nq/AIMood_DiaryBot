"""
Тестовый скрипт для проверки инициализации бота
"""

import sys
import os

# Добавляем путь к модулям приложения
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.bot.bot import mood_bot
from app.core.config import settings


def test_bot_initialization():
    """Тестирование инициализации бота"""
    print("🧪 Тестирование Telegram Bot...")
    
    # Проверяем токен
    if not settings.TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram Bot Token не настроен")
        print("ℹ️ Бот будет работать только после настройки токена в .env файле")
    else:
        print("✅ Telegram Bot Token настроен")
    
    # Пытаемся настроить приложение
    try:
        application = mood_bot.setup_application()
        
        if application:
            print("✅ Telegram Bot приложение настроено успешно")
            print(f"📋 Зарегистрированных обработчиков: {len(application.handlers[0])}")
            
            # Выводим список команд
            commands = [
                "/start - Начать работу с ботом",
                "/help - Справка", 
                "/mood - Записать настроение",
                "/stats - Статистика",
                "/recommendations - Рекомендации",
                "/analytics - Аналитика"
            ]
            
            print("\n🤖 Доступные команды:")
            for cmd in commands:
                print(f"  • {cmd}")
                
        else:
            print("❌ Не удалось настроить Telegram Bot приложение")
            
    except Exception as e:
        print(f"❌ Ошибка настройки бота: {e}")
    
    print("\n🎉 Тестирование завершено!")
    print("💡 Для запуска бота используйте: python run_bot.py")


if __name__ == "__main__":
    test_bot_initialization()