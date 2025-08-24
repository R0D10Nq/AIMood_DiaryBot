# 🚀 Руководство по развертыванию

## Содержание
- [Предварительные требования](#предварительные-требования)
- [Разработка](#разработка)
- [Подготовка к продакшену](#подготовка-к-продакшену)
- [Развертывание в продакшене](#развертывание-в-продакшене)
- [Мониторинг и обслуживание](#мониторинг-и-обслуживание)
- [Устранение неполадок](#устранение-неполадок)

## Предварительные требования

### Системные требования
- **ОС**: Linux (Ubuntu 20.04+, CentOS 8+) или macOS
- **CPU**: 2+ ядра
- **RAM**: 4GB+ (8GB+ для продакшена)
- **Диск**: 20GB+ свободного места
- **Сеть**: Стабильное интернет-соединение

### Необходимое ПО
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** 2.25+
- **Make** (опционально)

### API ключи (обязательно)
- **Telegram Bot Token** - получить у [@BotFather](https://t.me/botfather)
- **Google Gemini API Key** - получить в [Google AI Studio](https://makersuite.google.com/)

## Разработка

### 1. Клонирование и настройка
```bash
# Клонирование репозитория
git clone https://github.com/yourusername/ai-mood-diary-bot.git
cd ai-mood-diary-bot

# Настройка окружения
cp .env.example .env
```

### 2. Конфигурация .env файла
```bash
# Обязательные параметры
TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_key_here

# База данных (для разработки)
POSTGRES_DB=mood_diary_dev
POSTGRES_USER=mood_user
POSTGRES_PASSWORD=mood_password_dev

# Безопасность
SECRET_KEY=your-development-secret-key

# Разработка
ENVIRONMENT=development
DEBUG=true
```

### 3. Запуск для разработки
```bash
# Через Makefile
make dev

# Или напрямую через Docker Compose
docker-compose up -d --build

# Просмотр логов
make dev-logs
# или
docker-compose logs -f
```

### 4. Проверка работоспособности
- 🌐 **Frontend**: http://localhost
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 🗄️ **Database**: localhost:5432
- ⚡ **Redis**: localhost:6379

## Подготовка к продакшену

### 1. Безопасность
```bash
# Создание сильных паролей
openssl rand -base64 32  # для SECRET_KEY
openssl rand -base64 16  # для паролей БД

# Настройка firewall (Ubuntu)
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
```

### 2. SSL сертификаты
```bash
# Установка Certbot
sudo apt install certbot

# Получение SSL сертификата
sudo certbot certonly --standalone -d yourdomain.com

# Копирование в проект
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*.pem
```

### 3. Конфигурация продакшена
```bash
# Создание продакшен конфигурации
cp .env.prod.example .env.prod

# Редактирование с реальными значениями
nano .env.prod
```

**Пример .env.prod:**
```bash
# API ключи (ОБЯЗАТЕЛЬНО)
TELEGRAM_BOT_TOKEN=your_production_bot_token
GEMINI_API_KEY=your_production_gemini_key

# База данных
POSTGRES_DB=mood_diary_prod
POSTGRES_USER=mood_user_prod
POSTGRES_PASSWORD=very_strong_password_123

# Redis
REDIS_PASSWORD=very_strong_redis_password_456

# Безопасность
SECRET_KEY=super-strong-secret-key-for-production

# Домен
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Производительность
WORKERS=4
LOG_LEVEL=INFO

# Окружение
ENVIRONMENT=production
DEBUG=false
```

## Развертывание в продакшене

### Автоматическое развертывание
```bash
# Выполнение скрипта развертывания
chmod +x deploy-prod.sh
./deploy-prod.sh
```

### Ручное развертывание

#### 1. Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка для применения изменений
sudo reboot
```

#### 2. Развертывание приложения
```bash
# Загрузка базовых образов
docker-compose -f docker-compose.prod.yml pull postgres redis

# Сборка приложения
docker-compose -f docker-compose.prod.yml build --no-cache

# Запуск продакшен сервисов
docker-compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps
```

#### 3. Инициализация базы данных
```bash
# Выполнение миграций
docker-compose -f docker-compose.prod.yml exec backend python -c "
import asyncio
from app.database.database import init_db
asyncio.run(init_db())
"

# Создание бэкапа
make backup-prod
```

### Проверка развертывания
```bash
# Проверка health check
curl -f https://yourdomain.com/health

# Проверка API
curl -f https://yourdomain.com/api/health

# Проверка логов
docker-compose -f docker-compose.prod.yml logs --tail=50
```

## Обновления

### Обновление приложения
```bash
# Получение обновлений
git pull origin main

# Создание бэкапа перед обновлением
make backup-prod

# Обновление сервисов
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --build

# Проверка работоспособности
make status
```

### Откат версии
```bash
# Просмотр коммитов
git log --oneline -10

# Откат к предыдущей версии
git checkout COMMIT_HASH
./deploy-prod.sh

# Восстановление из бэкапа (если нужно)
docker-compose -f docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB < backup_20240101_120000.sql
```

## Мониторинг и обслуживание

### Логи
```bash
# Просмотр всех логов
make prod-logs

# Логи конкретного сервиса
make logs-backend
make logs-frontend
make logs-bot
make logs-db

# Поиск в логах
docker-compose -f docker-compose.prod.yml logs | grep ERROR
```

### Мониторинг ресурсов
```bash
# Использование ресурсов контейнерами
docker stats

# Размер образов и контейнеров
docker system df

# Мониторинг дискового пространства
df -h

# Мониторинг процессов
htop
```

### Автоматические бэкапы
```bash
# Ручной бэкап
make backup-prod

# Настройка cron для автоматических бэкапов (выполняется скриптом развертывания)
# Ежедневно в 2:00
0 2 * * * cd /path/to/project && make backup-prod

# Очистка старых бэкапов (старше 30 дней)
0 3 * * * find /opt/mood-diary/backups -name "backup_*.sql.gz" -mtime +30 -delete
```

### Проверка здоровья системы
```bash
# Проверка всех сервисов
make status

# Проверка базы данных
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Проверка Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Проверка интернет-соединения
curl -I https://api.telegram.org/
```

## Масштабирование

### Горизонтальное масштабирование
```bash
# Увеличение количества реплик backend
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Использование Docker Swarm
docker swarm init
docker stack deploy -c docker-compose.prod.yml mood-diary
```

### Вертикальное масштабирование
```yaml
# В docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
```

## Устранение неполадок

### Частые проблемы

#### 1. Сервисы не запускаются
```bash
# Проверка логов
docker-compose -f docker-compose.prod.yml logs

# Проверка портов
netstat -tulpn | grep :80
netstat -tulpn | grep :8000

# Перезапуск сервисов
docker-compose -f docker-compose.prod.yml restart
```

#### 2. База данных недоступна
```bash
# Проверка статуса PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Подключение к базе
docker-compose -f docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB

# Проверка логов PostgreSQL
docker-compose -f docker-compose.prod.yml logs postgres
```

#### 3. Telegram Bot не отвечает
```bash
# Проверка токена
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"

# Проверка webhook
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"

# Перезапуск бота
docker-compose -f docker-compose.prod.yml restart telegram_bot
```

#### 4. Frontend не загружается
```bash
# Проверка nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Проверка статических файлов
docker-compose -f docker-compose.prod.yml exec frontend ls -la /usr/share/nginx/html

# Перезапуск frontend
docker-compose -f docker-compose.prod.yml restart frontend nginx
```

### Диагностические команды
```bash
# Полная диагностика
make monitor

# Проверка сетевых подключений
docker network ls
docker network inspect mood_network_prod

# Проверка volumes
docker volume ls
docker volume inspect mood_diary_postgres_data_prod

# Системная информация
docker info
docker version
```

### Аварийное восстановление
```bash
# Остановка всех сервисов
docker-compose -f docker-compose.prod.yml down

# Восстановление из бэкапа
docker-compose -f docker-compose.prod.yml up -d postgres
sleep 30
docker-compose -f docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB < latest_backup.sql

# Полная пересборка
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a
./deploy-prod.sh
```

## Контакты и поддержка

- 📧 **Email**: support@mooddiary.app
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/ai-mood-diary-bot/issues)
- 📚 **Wiki**: [Project Wiki](https://github.com/yourusername/ai-mood-diary-bot/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-mood-diary-bot/discussions)