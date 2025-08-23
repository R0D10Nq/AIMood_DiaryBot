"""
Сервис для работы с Google Gemini AI
Анализ эмоций, тональности и генерация рекомендаций
"""

import google.generativeai as genai
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Сервис для работы с Google Gemini AI"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Инициализация клиента Gemini AI"""
        if not self.api_key:
            logger.warning("⚠️ Gemini API ключ не настроен")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info("✅ Gemini AI клиент инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Gemini AI: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Проверка доступности сервиса"""
        return self.model is not None and bool(self.api_key)
    
    async def analyze_mood_text(self, text: str, mood_score: float) -> Dict[str, Any]:
        """
        Анализ текста настроения с помощью Gemini AI
        
        Args:
            text: Текст описания настроения от пользователя
            mood_score: Оценка настроения от 1 до 10
            
        Returns:
            Словарь с результатами анализа
        """
        if not self.is_available():
            logger.warning("Gemini AI недоступен, возвращаю mock данные")
            return self._get_mock_analysis(text, mood_score)
        
        start_time = time.time()
        
        try:
            # Создаем промпт для анализа
            prompt = self._create_analysis_prompt(text, mood_score)
            
            # Отправляем запрос к Gemini
            response = self.model.generate_content(prompt)
            
            processing_time = time.time() - start_time
            
            # Парсим ответ
            analysis_result = self._parse_analysis_response(response.text)
            analysis_result["processing_time"] = processing_time
            analysis_result["ai_model"] = self.model_name
            
            logger.info(f"✅ Анализ выполнен за {processing_time:.2f}с")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа Gemini AI: {e}")
            processing_time = time.time() - start_time
            return self._get_fallback_analysis(text, mood_score, processing_time)
    
    def _create_analysis_prompt(self, text: str, mood_score: float) -> str:
        """Создание промпта для анализа настроения"""
        return f"""
Ты - эксперт психолог, специализирующийся на анализе эмоций и настроения. 
Проанализируй следующий текст о настроении пользователя и верни результат СТРОГО в JSON формате.

Текст пользователя: "{text}"
Оценка настроения (1-10): {mood_score}

Верни JSON со следующими полями:
{{
    "sentiment_score": число от -1 до 1 (негативное/позитивное),
    "sentiment_label": "positive" | "negative" | "neutral",
    "emotions": {{
        "радость": значение от 0 до 1,
        "грусть": значение от 0 до 1,
        "тревога": значение от 0 до 1,
        "спокойствие": значение от 0 до 1,
        "раздражение": значение от 0 до 1,
        "воодушевление": значение от 0 до 1
    }},
    "dominant_emotion": "название доминирующей эмоции",
    "keywords": ["ключевое_слово1", "ключевое_слово2", "ключевое_слово3"],
    "themes": ["тема1", "тема2"],
    "recommendations": "Персональные рекомендации для улучшения настроения (2-3 предложения)",
    "insights": "Краткий анализ эмоционального состояния (1-2 предложения)",
    "confidence_score": число от 0 до 1
}}

Отвечай ТОЛЬКО JSON, без дополнительного текста. Рекомендации и инсайты на русском языке.
"""
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Парсинг ответа от Gemini AI"""
        try:
            # Извлекаем JSON из ответа
            response_text = response_text.strip()
            
            # Иногда Gemini обрамляет JSON в ```json блоки
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Парсим JSON
            analysis = json.loads(response_text)
            
            # Валидируем структуру
            required_fields = [
                "sentiment_score", "sentiment_label", "emotions", 
                "dominant_emotion", "keywords", "themes", 
                "recommendations", "insights", "confidence_score"
            ]
            
            for field in required_fields:
                if field not in analysis:
                    logger.warning(f"Отсутствует поле {field} в ответе Gemini")
                    analysis[field] = self._get_default_value(field)
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON от Gemini: {e}")
            logger.error(f"Ответ: {response_text[:500]}...")
            raise
        except Exception as e:
            logger.error(f"Ошибка обработки ответа Gemini: {e}")
            raise
    
    def _get_default_value(self, field: str) -> Any:
        """Получить значение по умолчанию для поля"""
        defaults = {
            "sentiment_score": 0.0,
            "sentiment_label": "neutral",
            "emotions": {
                "радость": 0.3,
                "грусть": 0.2,
                "тревога": 0.2,
                "спокойствие": 0.3,
                "раздражение": 0.1,
                "воодушевление": 0.2
            },
            "dominant_emotion": "спокойствие",
            "keywords": ["настроение", "день"],
            "themes": ["повседневность"],
            "recommendations": "Рекомендуется больше времени проводить на свежем воздухе и заниматься физической активностью.",
            "insights": "Эмоциональное состояние находится в пределах нормы.",
            "confidence_score": 0.5
        }
        return defaults.get(field, None)
    
    def _get_mock_analysis(self, text: str, mood_score: float) -> Dict[str, Any]:
        """Возвращает mock данные когда Gemini недоступен"""
        # Простой анализ на основе оценки настроения
        if mood_score >= 7:
            sentiment_score = 0.7
            sentiment_label = "positive"
            dominant_emotion = "радость"
        elif mood_score >= 4:
            sentiment_score = 0.0
            sentiment_label = "neutral"
            dominant_emotion = "спокойствие"
        else:
            sentiment_score = -0.7
            sentiment_label = "negative"
            dominant_emotion = "грусть"
        
        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "emotions": {
                "радость": max(0.1, (mood_score - 5) / 5),
                "грусть": max(0.1, (5 - mood_score) / 5),
                "тревога": 0.2,
                "спокойствие": 0.4,
                "раздражение": 0.1,
                "воодушевление": max(0.1, (mood_score - 6) / 4)
            },
            "dominant_emotion": dominant_emotion,
            "keywords": ["настроение", "день", "эмоции"],
            "themes": ["ежедневная жизнь"],
            "recommendations": "Попробуйте медитацию или прогулку на свежем воздухе для улучшения настроения.",
            "insights": f"Текущая оценка настроения {mood_score}/10 говорит о {'хорошем' if mood_score >= 6 else 'среднем' if mood_score >= 4 else 'низком'} эмоциональном состоянии.",
            "confidence_score": 0.6,
            "processing_time": 0.1,
            "ai_model": "mock"
        }
    
    def _get_fallback_analysis(self, text: str, mood_score: float, processing_time: float) -> Dict[str, Any]:
        """Fallback анализ при ошибке Gemini"""
        analysis = self._get_mock_analysis(text, mood_score)
        analysis["processing_time"] = processing_time
        analysis["ai_model"] = f"{self.model_name}_fallback"
        analysis["recommendations"] = "Извините, анализ временно недоступен. Рекомендуем обратиться к специалисту при необходимости."
        return analysis
    
    async def generate_daily_insights(self, mood_entries: List[Dict[str, Any]]) -> str:
        """
        Генерация ежедневных инсайтов на основе нескольких записей
        
        Args:
            mood_entries: Список записей настроения за период
            
        Returns:
            Текст с инсайтами и рекомендациями
        """
        if not self.is_available() or not mood_entries:
            return "Недостаточно данных для анализа тенденций."
        
        try:
            # Создаем промпт для анализа тенденций
            prompt = self._create_insights_prompt(mood_entries)
            
            response = self.model.generate_content(prompt)
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Ошибка генерации инсайтов: {e}")
            return "Анализ тенденций временно недоступен."
    
    def _create_insights_prompt(self, mood_entries: List[Dict[str, Any]]) -> str:
        """Создание промпта для анализа тенденций"""
        entries_text = ""
        for entry in mood_entries[-7:]:  # Последние 7 записей
            entries_text += f"Дата: {entry.get('date', 'неизвестно')}, Оценка: {entry.get('mood_score', 0)}/10, Текст: {entry.get('mood_text', '')[:100]}...\n"
        
        return f"""
Ты - опытный психолог. Проанализируй записи настроения пользователя за последнее время и дай краткие инсайты.

Записи пользователя:
{entries_text}

Напиши краткий анализ (3-4 предложения) включающий:
1. Общий тренд настроения
2. Выявленные паттерны
3. Одну конкретную рекомендацию

Отвечай дружелюбно, на русском языке, без излишнего жаргона.
"""


# Создаем экземпляр сервиса
gemini_service = GeminiService()