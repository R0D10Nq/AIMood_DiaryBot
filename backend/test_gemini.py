"""
Тестовый скрипт для проверки работы Gemini AI
"""

import asyncio
import os
import sys

# Добавляем путь к модулям приложения
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.gemini_service import gemini_service


async def test_gemini_service():
    """Тестирование сервиса Gemini AI"""
    print("🧪 Тестирование Gemini AI сервиса...")
    
    # Проверяем доступность
    if not gemini_service.is_available():
        print("⚠️ Gemini AI недоступен (нет API ключа), тестируем mock режим")
    else:
        print("✅ Gemini AI доступен")
    
    # Тестовые данные
    test_cases = [
        {
            "text": "Сегодня был отличный день! Встретился с друзьями, погуляли в парке, поели мороженое. Настроение прекрасное!",
            "mood_score": 8.5
        },
        {
            "text": "Чувствую себя уставшим и подавленным. Работа не идет, проблемы дома. Хочется просто спать.",
            "mood_score": 3.0
        },
        {
            "text": "Обычный день, ничего особенного. Работал, ужинал, смотрел телевизор.",
            "mood_score": 5.5
        }
    ]
    
    # Тестируем каждый случай
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Тест {i} ---")
        print(f"Текст: {case['text'][:50]}...")
        print(f"Оценка: {case['mood_score']}")
        
        try:
            result = await gemini_service.analyze_mood_text(
                case['text'], 
                case['mood_score']
            )
            
            print(f"✅ Анализ завершен за {result.get('processing_time', 0):.2f}с")
            print(f"Тональность: {result.get('sentiment_label')} ({result.get('sentiment_score'):.2f})")
            print(f"Доминирующая эмоция: {result.get('dominant_emotion')}")
            print(f"Ключевые слова: {', '.join(result.get('keywords', []))}")
            print(f"Рекомендации: {result.get('recommendations', '')[:100]}...")
            print(f"Уверенность: {result.get('confidence_score', 0):.2f}")
            
        except Exception as e:
            print(f"❌ Ошибка при анализе: {e}")
    
    print("\n🎉 Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(test_gemini_service())