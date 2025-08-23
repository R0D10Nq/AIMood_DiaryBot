"""
Основной роутер API
Объединяет все endpoint'ы приложения
"""

from fastapi import APIRouter

# Создание основного роутера
api_router = APIRouter()

# Временные endpoint'ы для тестирования
@api_router.get("/status")
async def get_status():
    """Статус API"""
    return {
        "status": "active",
        "message": "API работает корректно! 🚀"
    }


@api_router.get("/test")
async def test_endpoint():
    """Тестовый endpoint"""
    return {
        "message": "Тестовый endpoint работает! ✅",
        "features": [
            "FastAPI backend",
            "SQLite database", 
            "Telegram Bot integration",
            "Gemini AI analysis",
            "Vue.js frontend"
        ]
    }


# Здесь будут подключены другие роутеры:
# api_router.include_router(mood_router, prefix="/mood", tags=["mood"])
# api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
# api_router.include_router(user_router, prefix="/users", tags=["users"])