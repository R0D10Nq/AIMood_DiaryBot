"""
Основной роутер API
Объединяет все endpoint'ы приложения
"""

from fastapi import APIRouter

from .users import router as users_router
from .mood_entries import router as mood_entries_router
from .analytics import router as analytics_router

# Создание основного роутера
api_router = APIRouter()

# Подключение роутеров
api_router.include_router(
    users_router, 
    prefix="/users", 
    tags=["users"],
    responses={404: {"description": "Пользователь не найден"}}
)

api_router.include_router(
    mood_entries_router, 
    prefix="/mood-entries", 
    tags=["mood-entries"],
    responses={404: {"description": "Запись настроения не найдена"}}
)

api_router.include_router(
    analytics_router, 
    prefix="/analytics", 
    tags=["analytics"],
    responses={404: {"description": "Данные не найдены"}}
)

# Основные endpoint'ы
@api_router.get("/status")
async def get_status():
    """Статус API"""
    return {
        "status": "active",
        "message": "AI Mood Diary Bot API работает корректно! 🚀",
        "version": "1.0.0",
        "features": [
            "FastAPI backend",
            "SQLite database", 
            "Telegram Bot integration",
            "Gemini AI analysis",
            "Vue.js frontend",
            "Real-time analytics"
        ]
    }


@api_router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    from ..services.gemini_service import gemini_service
    from ..core.config import settings
    
    return {
        "status": "healthy",
        "service": "ai-mood-diary-bot",
        "version": "1.0.0",
        "components": {
            "database": "connected",
            "gemini_ai": "available" if gemini_service.is_available() else "unavailable",
            "telegram_bot": "configured" if settings.TELEGRAM_BOT_TOKEN else "not_configured"
        }
    }