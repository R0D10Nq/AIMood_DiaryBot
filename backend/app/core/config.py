"""
Конфигурация приложения
Все настройки загружаются из переменных окружения
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    PROJECT_NAME: str = "AI Mood Diary Bot"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Сервер
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # База данных
    DATABASE_URL: str = "sqlite:///./mood_diary.db"
    
    # Безопасность
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    BOT_WEBHOOK_URL: str = ""
    BOT_WEBHOOK_PATH: str = "/webhook"
    
    # Google Gemini AI
    GEMINI_API_KEY: str = ""
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    
    # Аналитика
    ENABLE_ANALYTICS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Преобразование CORS_ORIGINS из строки в список
        if isinstance(self.CORS_ORIGINS, str):
            self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Проверка режима разработки"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Проверка продакшн режима"""
        return self.ENVIRONMENT.lower() == "production"


# Глобальный экземпляр настроек
settings = Settings()