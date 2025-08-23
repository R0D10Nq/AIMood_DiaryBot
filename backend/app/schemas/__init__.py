"""
Pydantic схемы для валидации данных API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# === USER SCHEMAS ===

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    telegram_id: int = Field(..., description="ID пользователя в Telegram")
    username: Optional[str] = Field(None, max_length=100, description="Username в Telegram")
    first_name: Optional[str] = Field(None, max_length=100, description="Имя")
    last_name: Optional[str] = Field(None, max_length=100, description="Фамилия")
    language_code: str = Field(default="ru", max_length=10, description="Код языка")
    timezone: str = Field(default="UTC", max_length=50, description="Часовой пояс")


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    pass


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    username: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    language_code: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    notifications_enabled: Optional[bool] = None


class User(UserBase):
    """Полная схема пользователя"""
    id: int
    mood_entries_count: int = 0
    is_active: bool = True
    notifications_enabled: bool = True
    created_at: datetime
    last_activity: datetime

    class Config:
        from_attributes = True


# === MOOD ENTRY SCHEMAS ===

class MoodEntryBase(BaseModel):
    """Базовая схема записи настроения"""
    mood_score: float = Field(..., ge=1, le=10, description="Оценка настроения от 1 до 10")
    mood_text: str = Field(..., min_length=1, max_length=5000, description="Описание настроения")
    activities: Optional[List[str]] = Field(None, description="Список активностей")
    weather: Optional[str] = Field(None, max_length=50, description="Погода")
    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="Количество часов сна")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Уровень стресса")
    entry_date: datetime = Field(..., description="Дата записи")


class MoodEntryCreate(MoodEntryBase):
    """Схема для создания записи настроения"""
    pass


class MoodEntryUpdate(BaseModel):
    """Схема для обновления записи настроения"""
    mood_score: Optional[float] = Field(None, ge=1, le=10)
    mood_text: Optional[str] = Field(None, min_length=1, max_length=5000)
    activities: Optional[List[str]] = None
    weather: Optional[str] = Field(None, max_length=50)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    stress_level: Optional[int] = Field(None, ge=1, le=10)


class MoodEntry(MoodEntryBase):
    """Полная схема записи настроения"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === AI ANALYSIS SCHEMAS ===

class AIAnalysisBase(BaseModel):
    """Базовая схема AI анализа"""
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="Тональность от -1 до 1")
    sentiment_label: Optional[str] = Field(None, description="Метка тональности")
    emotions: Optional[Dict[str, float]] = Field(None, description="Эмоции и их интенсивность")
    dominant_emotion: Optional[str] = Field(None, description="Доминирующая эмоция")
    keywords: Optional[List[str]] = Field(None, description="Ключевые слова")
    themes: Optional[List[str]] = Field(None, description="Темы")
    recommendations: Optional[str] = Field(None, description="Рекомендации")
    insights: Optional[str] = Field(None, description="Инсайты")


class AIAnalysisCreate(AIAnalysisBase):
    """Схема для создания AI анализа"""
    mood_entry_id: int
    ai_model: str = "gemini-1.5-flash"
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)


class AIAnalysis(AIAnalysisBase):
    """Полная схема AI анализа"""
    id: int
    user_id: int
    mood_entry_id: int
    ai_model: str
    processing_time: Optional[float]
    confidence_score: Optional[float]
    analyzed_at: datetime

    class Config:
        from_attributes = True


# === RESPONSE SCHEMAS ===

class MoodEntryWithAnalysis(MoodEntry):
    """Запись настроения с AI анализом"""
    ai_analysis: Optional[AIAnalysis] = None


class UserStats(BaseModel):
    """Статистика пользователя"""
    user_id: int
    total_entries: int
    average_mood: float
    mood_trend: str  # "improving", "declining", "stable"
    most_common_emotion: Optional[str]
    streak_days: int
    last_entry_date: Optional[datetime]


class MoodAnalytics(BaseModel):
    """Аналитика настроения"""
    period: str  # "week", "month", "year"
    average_mood: float
    mood_distribution: Dict[str, int]  # "positive", "neutral", "negative"
    emotion_trends: Dict[str, List[float]]
    recommendations_summary: List[str]


# === ERROR SCHEMAS ===

class ErrorResponse(BaseModel):
    """Схема ошибки"""
    detail: str
    error_code: Optional[str] = None


class ValidationError(BaseModel):
    """Схема ошибки валидации"""
    field: str
    message: str
    invalid_value: Any