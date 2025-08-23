# AI Mood Diary Bot 🤖💭

Интеллектуальный телеграм-бот для ведения дневника настроения с анализом эмоций через ИИ.

## Описание проекта

AI Mood Diary Bot - это современное решение для отслеживания эмоционального состояния пользователей. Бот анализирует записи о настроении с помощью Google Gemini AI и предоставляет детальную аналитику через веб-интерфейс.

### Основные функции:

- 📱 **Telegram Bot** - удобный интерфейс для ежедневных записей
- 🧠 **AI Анализ** - анализ эмоций через Gemini API
- 📊 **Веб Dashboard** - детальная аналитика и графики
- 🎯 **Рекомендации** - персональные советы для улучшения настроения
- 📈 **Статистика** - тренды настроения по дням/неделям/месяцам

## Технологический стек

### Backend:
- **FastAPI** - современный Python веб-фреймворк
- **SQLite** - локальная база данных
- **SQLAlchemy** - ORM для работы с БД
- **python-telegram-bot** - библиотека для Telegram Bot API
- **Google Gemini AI** - анализ эмоций и текста

### Frontend:
- **Vue.js 3** - прогрессивный JavaScript фреймворк
- **Vuetify** - Material Design компоненты
- **Chart.js** - графики и аналитика
- **Axios** - HTTP клиент

### DevOps:
- **Docker** - контейнеризация приложения
- **GitHub Actions** - CI/CD pipeline
- **Docker Compose** - оркестрация сервисов

## Установка и запуск

### Предварительные требования:
- Python 3.9+
- Node.js 16+
- Docker (опционально)

### Быстрый старт:

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ai-mood-diary-bot.git
cd ai-mood-diary-bot
```

2. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл, добавив API ключи
```

3. Запустите через Docker:
```bash
docker-compose up -d
```

Или установите зависимости и запустите вручную:
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev
```

### Переменные окружения:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./mood_diary.db
SECRET_KEY=your_secret_key
CORS_ORIGINS=http://localhost:3000
```

## Использование

### Telegram Bot команды:

- `/start` - начать работу с ботом
- `/mood` - записать настроение дня
- `/stats` - посмотреть краткую статистику
- `/help` - помощь по командам

### Веб-интерфейс:

Откройте http://localhost:3000 для доступа к dashboard с аналитикой.

## Структура проекта

```
ai-mood-diary-bot/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Настройки и конфигурация
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── services/       # Бизнес-логика
│   │   └── bot/            # Telegram bot
│   ├── requirements.txt
│   └── main.py
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue компоненты
│   │   ├── views/          # Страницы
│   │   ├── services/       # API сервисы
│   │   └── stores/         # Pinia stores
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml      # Docker конфигурация
├── .github/workflows/      # CI/CD pipeline
└── docs/                   # Документация
```

## API Документация

После запуска backend, API документация доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Разработка

### Настройка среды разработки:

1. Установите pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

2. Запустите тесты:
```bash
# Backend тесты
cd backend
pytest

# Frontend тесты
cd frontend
npm run test
```

## Контрибьюция

1. Форкните проект
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Добавил крутую фичу'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для деталей.

## Автор

Разработано с ❤️ для демонстрации навыков middle-разработчика.

---

*Проект создан в образовательных целях и демонстрирует интеграцию современных технологий для создания full-stack приложения с ИИ.*