"""
AI Mood Diary Bot - FastAPI Backend
Основное приложение для обработки API запросов и интеграции с Telegram Bot
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.api import api_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("🚀 Запускаю AI Mood Diary Bot backend...")
    
    # Создание таблиц в базе данных
    create_tables()
    logger.info("✅ База данных инициализирована")
    
    yield
    
    logger.info("🛑 Завершение работы backend...")


# Создание FastAPI приложения
app = FastAPI(
    title="AI Mood Diary Bot API",
    description="Backend API для интеллектуального дневника настроения с ИИ анализом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Глобальный обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Неожиданная ошибка: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )


# Основные маршруты
@app.get("/")
async def root():
    """Основной endpoint для проверки работы API"""
    return {
        "message": "AI Mood Diary Bot API работает! 🤖",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "ai-mood-diary-bot",
        "version": "1.0.0"
    }


# Подключение API роутера
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    logger.info("🔥 Запуск в режиме разработки...")
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
        log_level="info"
    )