"""
Сервис анализа настроения
Объединяет работу с базой данных и AI анализом
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from .gemini_service import gemini_service
from ..models.ai_analysis import AIAnalysis
from ..models.mood_entry import MoodEntry
from ..schemas import AIAnalysisCreate

logger = logging.getLogger(__name__)


class MoodAnalyzer:
    """Сервис для анализа настроения с сохранением в БД"""
    
    def __init__(self):
        self.ai_service = gemini_service
    
    async def analyze_and_save(
        self, 
        db: Session, 
        mood_entry: MoodEntry
    ) -> Optional[AIAnalysis]:
        """
        Анализирует запись настроения и сохраняет результат в БД
        
        Args:
            db: Сессия базы данных
            mood_entry: Запись настроения для анализа
            
        Returns:
            Созданный объект AIAnalysis или None при ошибке
        """
        try:
            logger.info(f"🧠 Начинаю анализ записи настроения ID: {mood_entry.id}")
            
            # Проводим AI анализ
            analysis_result = await self.ai_service.analyze_mood_text(
                text=mood_entry.mood_text,
                mood_score=mood_entry.mood_score
            )
            
            # Создаем запись в БД
            analysis_data = AIAnalysisCreate(
                mood_entry_id=mood_entry.id,
                sentiment_score=analysis_result.get("sentiment_score"),
                sentiment_label=analysis_result.get("sentiment_label"),
                emotions=analysis_result.get("emotions"),
                dominant_emotion=analysis_result.get("dominant_emotion"),
                keywords=analysis_result.get("keywords"),
                themes=analysis_result.get("themes"),
                recommendations=analysis_result.get("recommendations"),
                insights=analysis_result.get("insights"),
                ai_model=analysis_result.get("ai_model", "gemini-1.5-flash"),
                processing_time=analysis_result.get("processing_time"),
                confidence_score=analysis_result.get("confidence_score")
            )
            
            # Сохраняем в базу данных
            db_analysis = AIAnalysis(
                user_id=mood_entry.user_id,
                **analysis_data.model_dump()
            )
            
            db.add(db_analysis)
            db.commit()
            db.refresh(db_analysis)
            
            logger.info(f"✅ Анализ сохранен в БД с ID: {db_analysis.id}")
            return db_analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа настроения: {e}")
            db.rollback()
            return None
    
    def get_mood_summary(self, db: Session, user_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Получить сводку настроения пользователя за период
        
        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            days: Количество дней для анализа
            
        Returns:
            Словарь со сводкой настроения
        """
        try:
            # Получаем записи за период
            from ..crud.mood_entry import mood_entry_crud
            entries = mood_entry_crud.get_recent_entries(db, user_id, days)
            
            if not entries:
                return {
                    "period_days": days,
                    "total_entries": 0,
                    "message": "Нет записей за указанный период"
                }
            
            # Базовая статистика
            total_entries = len(entries)
            average_mood = sum(entry.mood_score for entry in entries) / total_entries
            
            # Анализ эмоций (из AI анализов)
            emotion_stats = {}
            sentiment_stats = {"positive": 0, "negative": 0, "neutral": 0}
            
            for entry in entries:
                if entry.ai_analysis:
                    # Статистика эмоций
                    if entry.ai_analysis.emotions:
                        for emotion, value in entry.ai_analysis.emotions.items():
                            if emotion not in emotion_stats:
                                emotion_stats[emotion] = []
                            emotion_stats[emotion].append(value)
                    
                    # Статистика тональности
                    sentiment = entry.ai_analysis.sentiment_label
                    if sentiment in sentiment_stats:
                        sentiment_stats[sentiment] += 1
            
            # Вычисляем средние значения эмоций
            avg_emotions = {}
            for emotion, values in emotion_stats.items():
                avg_emotions[emotion] = round(sum(values) / len(values), 2) if values else 0
            
            # Находим доминирующую эмоцию
            dominant_emotion = max(avg_emotions.items(), key=lambda x: x[1])[0] if avg_emotions else "неопределено"
            
            # Тренд настроения
            if len(entries) >= 3:
                recent_avg = sum(entry.mood_score for entry in entries[:3]) / 3
                older_avg = sum(entry.mood_score for entry in entries[-3:]) / 3
                
                if recent_avg > older_avg + 0.5:
                    trend = "улучшается 📈"
                elif recent_avg < older_avg - 0.5:
                    trend = "ухудшается 📉"
                else:
                    trend = "стабильно ➡️"
            else:
                trend = "недостаточно данных"
            
            return {
                "period_days": days,
                "total_entries": total_entries,
                "average_mood": round(average_mood, 1),
                "mood_trend": trend,
                "dominant_emotion": dominant_emotion,
                "emotion_averages": avg_emotions,
                "sentiment_distribution": sentiment_stats,
                "latest_entry_date": entries[0].entry_date.strftime("%d.%m.%Y") if entries else None
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения сводки настроения: {e}")
            return {
                "period_days": days,
                "error": "Ошибка при получении данных"
            }
    
    def get_recommendations_for_user(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Получить персональные рекомендации для пользователя
        
        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            
        Returns:
            Словарь с рекомендациями
        """
        try:
            from ..crud.mood_entry import mood_entry_crud
            
            # Получаем последние записи с анализом
            recent_entries = mood_entry_crud.get_recent_entries(db, user_id, 5)
            
            if not recent_entries:
                return {
                    "message": "Недостаточно данных для рекомендаций",
                    "recommendations": [
                        "Начните вести дневник настроения регулярно",
                        "Записывайте не только оценку, но и подробности дня"
                    ]
                }
            
            # Собираем рекомендации из AI анализов
            all_recommendations = []
            mood_scores = []
            
            for entry in recent_entries:
                mood_scores.append(entry.mood_score)
                if entry.ai_analysis and entry.ai_analysis.recommendations:
                    all_recommendations.append(entry.ai_analysis.recommendations)
            
            # Анализируем паттерны
            avg_mood = sum(mood_scores) / len(mood_scores)
            
            # Базовые рекомендации в зависимости от среднего настроения
            base_recommendations = []
            
            if avg_mood < 4:
                base_recommendations = [
                    "🌱 Рассмотрите возможность обращения к специалисту",
                    "🚶‍♀️ Попробуйте ежедневные прогулки на свежем воздухе",
                    "🧘‍♀️ Практикуйте техники релаксации или медитацию"
                ]
            elif avg_mood < 6:
                base_recommendations = [
                    "💪 Добавьте физическую активность в свой день",
                    "👥 Проводите больше времени с близкими людьми",
                    "🎯 Поставьте себе небольшие достижимые цели"
                ]
            else:
                base_recommendations = [
                    "✨ Продолжайте в том же духе!",
                    "📚 Попробуйте изучить что-то новое",
                    "🤝 Поделитесь своим позитивом с окружающими"
                ]
            
            return {
                "average_mood": round(avg_mood, 1),
                "period": "последние 5 записей",
                "ai_recommendations": all_recommendations[-3:] if all_recommendations else [],
                "general_recommendations": base_recommendations,
                "total_entries_analyzed": len(recent_entries)
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения рекомендаций: {e}")
            return {
                "error": "Ошибка при получении рекомендаций",
                "general_recommendations": [
                    "Ведите регулярный дневник настроения",
                    "Занимайтесь физической активностью",
                    "Поддерживайте социальные связи"
                ]
            }


# Создаем экземпляр анализатора
mood_analyzer = MoodAnalyzer()