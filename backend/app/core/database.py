"""
Настройка подключения к базе данных SQLite
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.is_development  # Включаем логи SQL в режиме разработки
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Метаданные для миграций
metadata = MetaData()


def get_db():
    """
    Зависимость для получения сессии базы данных
    Используется в FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Создание всех таблиц в базе данных"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы базы данных созданы успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка создания таблиц: {e}")
        raise


def drop_tables():
    """Удаление всех таблиц (используется для тестов)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("🗑️ Таблицы базы данных удалены")
    except Exception as e:
        logger.error(f"❌ Ошибка удаления таблиц: {e}")
        raise