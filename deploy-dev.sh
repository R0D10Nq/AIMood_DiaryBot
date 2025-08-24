#!/bin/bash

# Development Deployment Script
echo "🚀 Starting AI Mood Diary Bot development deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual values before continuing!"
    echo "   Required: TELEGRAM_BOT_TOKEN, GEMINI_API_KEY"
    read -p "Press Enter after editing .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/logs backend/data database nginx/ssl

# Build and start services
echo "🔨 Building and starting services..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Show service URLs
echo ""
echo "✅ Development deployment completed!"
echo ""
echo "🌐 Service URLs:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Database: localhost:5432"
echo "   Redis: localhost:6379"
echo ""
echo "📊 To view logs:"
echo "   All services: docker-compose logs -f"
echo "   Backend: docker-compose logs -f backend"
echo "   Frontend: docker-compose logs -f frontend"
echo "   Bot: docker-compose logs -f telegram_bot"
echo ""
echo "🛑 To stop services: docker-compose down"
echo ""

# Check if services are responding
echo "🏥 Health check..."
sleep 5
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

if curl -f http://localhost/health &> /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
fi

echo ""
echo "🎉 Deployment completed! Check the logs if any service is not working properly."