"""
Модель анализа настроения с помощью ИИ
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base


class AIAnalysis(Base):
    """
    Модель анализа настроения с помощью Gemini AI
    Хранит результаты анализа эмоций, тональности и рекомендации
    """
    __tablename__ = "ai_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="ID пользователя")
    mood_entry_id = Column(Integer, ForeignKey("mood_entries.id"), nullable=False, comment="ID записи настроения")
    
    # Результаты анализа
    sentiment_score = Column(Float, nullable=True, comment="Тональность текста от -1 до 1")
    sentiment_label = Column(String(20), nullable=True, comment="Метка тональности: positive/negative/neutral")
    
    # Эмоции
    emotions = Column(JSON, nullable=True, comment="Обнаруженные эмоции и их интенсивность")
    dominant_emotion = Column(String(50), nullable=True, comment="Доминирующая эмоция")
    
    # Анализ контента
    keywords = Column(JSON, nullable=True, comment="Ключевые слова из текста")
    themes = Column(JSON, nullable=True, comment="Обнаруженные темы")
    
    # Рекомендации ИИ
    recommendations = Column(Text, nullable=True, comment="Рекомендации от ИИ")
    insights = Column(Text, nullable=True, comment="Инсайты и анализ")
    
    # Метаданные
    ai_model = Column(String(50), default="gemini-1.5-flash", comment="Модель ИИ, которая провела анализ")
    processing_time = Column(Float, nullable=True, comment="Время обработки в секундах")
    confidence_score = Column(Float, nullable=True, comment="Уверенность ИИ в анализе от 0 до 1")
    
    # Даты
    analyzed_at = Column(DateTime, default=datetime.utcnow, comment="Дата и время анализа")
    
    # Связи
    user = relationship("User", back_populates="ai_analyses")
    mood_entry = relationship("MoodEntry", back_populates="ai_analysis")
    
    def __repr__(self):
        return f"<AIAnalysis(id={self.id}, mood_entry_id={self.mood_entry_id}, sentiment={self.sentiment_label})>"
    
    def to_dict(self):
        """Преобразование объекта в словарь для JSON ответов"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mood_entry_id": self.mood_entry_id,
            "sentiment_score": self.sentiment_score,
            "sentiment_label": self.sentiment_label,
            "emotions": self.emotions,
            "dominant_emotion": self.dominant_emotion,
            "keywords": self.keywords,
            "themes": self.themes,
            "recommendations": self.recommendations,
            "insights": self.insights,
            "ai_model": self.ai_model,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None
        }