"""
Модель записи настроения
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base


class MoodEntry(Base):
    """
    Модель записи настроения пользователя
    Основная сущность для хранения ежедневных записей о настроении
    """
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="ID пользователя")
    
    # Основные данные
    mood_score = Column(Float, nullable=False, comment="Оценка настроения от 1 до 10")
    mood_text = Column(Text, nullable=False, comment="Описание настроения от пользователя")
    
    # Дополнительная информация
    activities = Column(JSON, nullable=True, comment="Список активностей дня")
    weather = Column(String(50), nullable=True, comment="Погода")
    sleep_hours = Column(Float, nullable=True, comment="Количество часов сна")
    stress_level = Column(Integer, nullable=True, comment="Уровень стресса от 1 до 10")
    
    # Даты
    entry_date = Column(DateTime, nullable=False, comment="Дата записи (день, за который делается запись)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Дата создания записи")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Дата обновления")
    
    # Связи
    user = relationship("User", back_populates="mood_entries")
    ai_analysis = relationship("AIAnalysis", back_populates="mood_entry", uselist=False)
    
    def __repr__(self):
        return f"<MoodEntry(id={self.id}, user_id={self.user_id}, mood_score={self.mood_score}, date={self.entry_date})>"
    
    def to_dict(self):
        """Преобразование объекта в словарь для JSON ответов"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mood_score": self.mood_score,
            "mood_text": self.mood_text,
            "activities": self.activities,
            "weather": self.weather,
            "sleep_hours": self.sleep_hours,
            "stress_level": self.stress_level,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "ai_analysis": self.ai_analysis.to_dict() if self.ai_analysis else None
        }