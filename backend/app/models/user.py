"""
Модель пользователя
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base


class User(Base):
    """
    Модель пользователя Telegram бота
    Хранит информацию о пользователях, которые используют бот
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False, comment="ID пользователя в Telegram")
    username = Column(String(100), nullable=True, comment="Username в Telegram")
    first_name = Column(String(100), nullable=True, comment="Имя пользователя")
    last_name = Column(String(100), nullable=True, comment="Фамилия пользователя")
    language_code = Column(String(10), default="ru", comment="Код языка пользователя")
    timezone = Column(String(50), default="UTC", comment="Часовой пояс пользователя")
    
    # Статистика
    mood_entries_count = Column(Integer, default=0, comment="Количество записей настроения")
    
    # Настройки
    is_active = Column(Boolean, default=True, comment="Активен ли пользователь")
    notifications_enabled = Column(Boolean, default=True, comment="Включены ли уведомления")
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow, comment="Дата регистрации")
    last_activity = Column(DateTime, default=datetime.utcnow, comment="Последняя активность")
    
    # Связи
    mood_entries = relationship("MoodEntry", back_populates="user", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"
    
    def to_dict(self):
        """Преобразование объекта в словарь для JSON ответов"""
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "language_code": self.language_code,
            "timezone": self.timezone,
            "mood_entries_count": self.mood_entries_count,
            "is_active": self.is_active,
            "notifications_enabled": self.notifications_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }