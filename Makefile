# AI Mood Diary Bot - Makefile
# Easy commands for development and deployment

.PHONY: help install dev prod stop clean logs test lint format security

# Default target
help:
	@echo "🤖 AI Mood Diary Bot - Available Commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make install        - Install all dependencies"
	@echo "  make setup-dev      - Setup development environment"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev            - Start development environment"
	@echo "  make dev-bg         - Start development in background"
	@echo "  make dev-logs       - Show development logs"
	@echo ""
	@echo "🏭 Production:"
	@echo "  make prod           - Deploy production environment"
	@echo "  make prod-bg        - Deploy production in background"
	@echo "  make prod-logs      - Show production logs"
	@echo ""
	@echo "🛠️  Management:"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make clean          - Clean up containers and volumes"
	@echo "  make status         - Show service status"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test           - Run all tests"
	@echo "  make test-backend   - Run backend tests only"
	@echo "  make test-frontend  - Run frontend tests only"
	@echo "  make lint           - Run linting checks"
	@echo "  make format         - Format code"
	@echo ""
	@echo "🔒 Security & Maintenance:"
	@echo "  make security       - Run security checks"
	@echo "  make backup         - Create database backup"
	@echo "  make update         - Update dependencies"
	@echo ""

# Installation
install:
	@echo "📦 Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	@echo "✅ Installation completed!"

setup-dev:
	@echo "🔧 Setting up development environment..."
	cp .env.example .env
	@echo "📝 Please edit .env file with your configuration"
	@echo "⚠️  Required: TELEGRAM_BOT_TOKEN, GEMINI_API_KEY"

# Development
dev:
	@echo "🚀 Starting development environment..."
	docker-compose up --build

dev-bg:
	@echo "🚀 Starting development environment in background..."
	docker-compose up -d --build
	@echo "✅ Development environment started!"
	@echo "🌐 Frontend: http://localhost"
	@echo "🔧 Backend: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

dev-logs:
	@echo "📋 Development logs:"
	docker-compose logs -f

# Production
prod:
	@echo "🏭 Deploying production environment..."
	chmod +x deploy-prod.sh
	./deploy-prod.sh

prod-bg:
	@echo "🏭 Starting production environment in background..."
	docker-compose -f docker-compose.prod.yml up -d --build

prod-logs:
	@echo "📋 Production logs:"
	docker-compose -f docker-compose.prod.yml logs -f

# Management
stop:
	@echo "🛑 Stopping all services..."
	docker-compose down
	docker-compose -f docker-compose.prod.yml down
	@echo "✅ All services stopped!"

restart:
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted!"

restart-prod:
	@echo "🔄 Restarting production services..."
	docker-compose -f docker-compose.prod.yml restart
	@echo "✅ Production services restarted!"

clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed!"

status:
	@echo "📊 Service Status:"
	@echo ""
	@echo "Development:"
	@docker-compose ps 2>/dev/null || echo "Development environment not running"
	@echo ""
	@echo "Production:"
	@docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo "Production environment not running"

# Testing
test:
	@echo "🧪 Running all tests..."
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test

# Code Quality
lint:
	@echo "🔍 Running linting checks..."
	@echo "Backend:"
	cd backend && python -m flake8 app/
	cd backend && python -m mypy app/
	@echo "Frontend:"
	cd frontend && npm run lint

format:
	@echo "✨ Formatting code..."
	@echo "Backend:"
	cd backend && python -m black app/
	cd backend && python -m isort app/
	@echo "Frontend:"
	cd frontend && npm run format

# Security
security:
	@echo "🔒 Running security checks..."
	@echo "Backend dependencies:"
	cd backend && python -m pip-audit
	@echo "Frontend dependencies:"
	cd frontend && npm audit
	@echo "Docker security:"
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PWD):/src \
		aquasec/trivy fs /src

# Maintenance
backup:
	@echo "💾 Creating database backup..."
	@timestamp=$$(date +%Y%m%d_%H%M%S) && \
	docker-compose exec postgres pg_dump -U $$POSTGRES_USER $$POSTGRES_DB > backup_$$timestamp.sql && \
	echo "✅ Backup saved as backup_$$timestamp.sql"

backup-prod:
	@echo "💾 Creating production database backup..."
	@timestamp=$$(date +%Y%m%d_%H%M%S) && \
	docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U $$POSTGRES_USER $$POSTGRES_DB > backup_prod_$$timestamp.sql && \
	echo "✅ Production backup saved as backup_prod_$$timestamp.sql"

update:
	@echo "📈 Updating dependencies..."
	@echo "Backend:"
	cd backend && pip install --upgrade -r requirements.txt
	@echo "Frontend:"
	cd frontend && npm update
	@echo "Docker images:"
	docker-compose pull
	docker-compose -f docker-compose.prod.yml pull

# Database management
db-reset:
	@echo "🗄️  Resetting development database..."
	docker-compose down postgres
	docker volume rm $$(docker volume ls -q | grep postgres) 2>/dev/null || true
	docker-compose up -d postgres
	@echo "✅ Database reset completed!"

db-migrate:
	@echo "🗄️  Running database migrations..."
	docker-compose exec backend python -c "from app.database.database import init_db; import asyncio; asyncio.run(init_db())"
	@echo "✅ Migrations completed!"

# Monitoring
monitor:
	@echo "📊 Service monitoring dashboard:"
	@echo ""
	watch -n 2 'docker-compose ps; echo ""; docker stats --no-stream'

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-bot:
	docker-compose logs -f telegram_bot

logs-db:
	docker-compose logs -f postgres

# SSL Setup (for production)
ssl-cert:
	@echo "🔒 Setting up SSL certificates..."
	@echo "Please ensure you have certbot installed"
	sudo certbot certonly --standalone -d your-domain.com
	sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
	sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
	sudo chown $$USER:$$USER nginx/ssl/*.pem
	@echo "✅ SSL certificates installed!"

# Quick development server (without Docker)
dev-backend:
	@echo "🚀 Starting backend development server..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "🚀 Starting frontend development server..."
	cd frontend && npm run dev

dev-bot:
	@echo "🤖 Starting bot development server..."
	cd backend && python -m app.bot.main