# API Документация

## Общие сведения

AI Mood Diary Bot предоставляет RESTful API для взаимодействия с системой отслеживания настроения.

### Базовый URL
```
http://localhost:8000/api
```

### Аутентификация
API использует стандартную аутентификацию через API ключи и JWT токены.

## Endpoints

### Users API

#### Получить пользователя
```http
GET /api/users/{user_id}
```

**Ответ:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "user123",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2024-01-01T12:00:00Z",
  "is_active": true,
  "mood_entries_count": 45
}
```

#### Создать пользователя
```http
POST /api/users/
```

**Тело запроса:**
```json
{
  "telegram_id": 123456789,
  "username": "user123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Mood Entries API

#### Получить записи настроения
```http
GET /api/mood-entries/?user_id={user_id}&limit={limit}&offset={offset}
```

**Параметры:**
- `user_id` (required): ID пользователя
- `limit` (optional): Количество записей (по умолчанию 50)
- `offset` (optional): Смещение (по умолчанию 0)
- `start_date` (optional): Начальная дата (YYYY-MM-DD)
- `end_date` (optional): Конечная дата (YYYY-MM-DD)

**Ответ:**
```json
{
  "entries": [
    {
      "id": 1,
      "user_id": 1,
      "mood_score": 7,
      "note": "Хороший день на работе",
      "emotions": ["радость", "спокойствие"],
      "activities": ["работа", "спорт"],
      "energy_level": 8,
      "stress_level": 3,
      "entry_date": "2024-01-01T12:00:00Z",
      "created_at": "2024-01-01T12:05:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "per_page": 50
}
```

#### Создать запись настроения
```http
POST /api/mood-entries/
```

**Тело запроса:**
```json
{
  "user_id": 1,
  "mood_score": 7,
  "note": "Хороший день на работе",
  "emotions": ["радость", "спокойствие"],
  "activities": ["работа", "спорт"],
  "energy_level": 8,
  "stress_level": 3,
  "entry_date": "2024-01-01T12:00:00Z"
}
```

#### Получить статистику пользователя
```http
GET /api/users/{user_id}/stats
```

**Ответ:**
```json
{
  "total_entries": 45,
  "average_mood": 6.8,
  "mood_trend": "improving",
  "streak_days": 7,
  "last_entry_date": "2024-01-15T12:00:00Z"
}
```

### Analytics API

#### Получить тренды настроения
```http
GET /api/analytics/mood-trends?user_id={user_id}&period={period}
```

**Параметры:**
- `user_id` (required): ID пользователя
- `period` (optional): Период анализа (week, month, quarter, year)

**Ответ:**
```json
{
  "period": "month",
  "mood_trend": [
    {
      "date": "2024-01-01",
      "average_mood": 6.5,
      "entries_count": 1
    }
  ],
  "emotion_trends": {
    "радость": [
      {"date": "2024-01-01", "value": 0.8}
    ]
  },
  "activity_correlations": {
    "спорт": 0.75,
    "работа": 0.45
  }
}
```

#### Получить аналитику по периоду
```http
GET /api/analytics/period-analysis?user_id={user_id}&start_date={start}&end_date={end}
```

#### Сгенерировать AI инсайты
```http
POST /api/analytics/generate-insights
```

**Тело запроса:**
```json
{
  "user_id": 1,
  "period_days": 30
}
```

**Ответ:**
```json
{
  "user_id": 1,
  "period_days": 30,
  "entries_analyzed": 25,
  "ai_insights": "За последний месяц ваше настроение показывает положительную динамику...",
  "summary": {
    "average_mood": 7.2,
    "mood_trend": "improving",
    "dominant_emotions": ["радость", "спокойствие"],
    "stress_factors": ["работа"],
    "recommendations": [
      "Продолжайте регулярные занятия спортом",
      "Рассмотрите возможность медитации для снижения стресса"
    ]
  },
  "generated_at": "2024-01-15T12:00:00Z"
}
```

### Health Check

#### Проверка состояния API
```http
GET /health
```

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "gemini_ai": "available"
  }
}
```

## Коды ошибок

### HTTP статус коды
- `200` - Успешный запрос
- `201` - Ресурс создан
- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `422` - Ошибка валидации
- `500` - Внутренняя ошибка сервера

### Формат ошибок
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "mood_score",
        "message": "Value must be between 1 and 10"
      }
    ]
  }
}
```

## Rate Limiting

API имеет ограничения на количество запросов:
- **Общие запросы**: 100 запросов в минуту
- **AI анализ**: 10 запросов в минуту
- **Создание записей**: 20 запросов в минуту

## WebSocket API

### Подключение к WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{user_id}');
```

### События
- `mood_entry_created` - Новая запись настроения
- `ai_analysis_complete` - Завершен AI анализ
- `reminder_scheduled` - Запланировано напоминание

## SDK и библиотеки

### Python SDK
```python
from mood_diary_sdk import MoodDiaryClient

client = MoodDiaryClient(api_key="your_api_key")
user = client.users.get(user_id=1)
entries = client.mood_entries.list(user_id=1, limit=10)
```

### JavaScript SDK
```javascript
import { MoodDiaryAPI } from 'mood-diary-js';

const api = new MoodDiaryAPI({
  baseURL: 'http://localhost:8000/api',
  apiKey: 'your_api_key'
});

const user = await api.users.get(1);
const entries = await api.moodEntries.list({ userId: 1, limit: 10 });
```

## Примеры использования

### Создание полного workflow
```python
# Создание пользователя
user = client.users.create({
    "telegram_id": 123456789,
    "username": "john_doe",
    "first_name": "John"
})

# Добавление записи настроения
entry = client.mood_entries.create({
    "user_id": user.id,
    "mood_score": 8,
    "note": "Отличный день!",
    "emotions": ["радость", "энергичность"],
    "activities": ["работа", "спорт"]
})

# Получение аналитики
trends = client.analytics.get_trends(user.id, period="month")
insights = client.analytics.generate_insights(user.id, period_days=30)
```

## Тестирование API

### Postman коллекция
Импортируйте коллекцию Postman из файла `docs/postman_collection.json`

### cURL примеры
```bash
# Получить пользователя
curl -X GET "http://localhost:8000/api/users/1" \
  -H "Authorization: Bearer your_token"

# Создать запись настроения
curl -X POST "http://localhost:8000/api/mood-entries/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "user_id": 1,
    "mood_score": 7,
    "note": "Хороший день",
    "emotions": ["радость"],
    "activities": ["работа"]
  }'
```