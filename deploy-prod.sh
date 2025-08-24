#!/bin/bash

# Production Deployment Script
echo "🚀 Starting AI Mood Diary Bot production deployment..."

# Check if running as root (not recommended for production)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running as root is not recommended for production!"
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check for production environment file
if [ ! -f .env.prod ]; then
    echo "📝 Creating .env.prod file from template..."
    cp .env.prod.example .env.prod
    echo "❌ Please edit .env.prod file with your production values!"
    echo "   Required: TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, SECRET_KEY, domain configuration"
    echo "   Security: Use strong passwords and secure secret keys"
    exit 1
fi

# Validate required environment variables
echo "🔍 Validating environment configuration..."
source .env.prod

required_vars=("TELEGRAM_BOT_TOKEN" "GEMINI_API_KEY" "SECRET_KEY" "POSTGRES_PASSWORD" "REDIS_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set in .env.prod"
        exit 1
    fi
done

# Create necessary directories with proper permissions
echo "📁 Creating production directories..."
sudo mkdir -p /opt/mood-diary/{database,nginx/ssl,logs,backups}
sudo chown -R $USER:$USER /opt/mood-diary

mkdir -p backend/logs backend/data database nginx/ssl

# Backup existing deployment if it exists
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "💾 Creating backup of existing deployment..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > "backup_${timestamp}.sql"
    echo "📦 Database backup saved as backup_${timestamp}.sql"
fi

# Pull latest images
echo "📥 Pulling latest base images..."
docker-compose -f docker-compose.prod.yml pull postgres redis nginx

# Build application images
echo "🔨 Building production images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Start production services
echo "🚀 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to initialize..."
sleep 30

# Run database migrations if needed
echo "🗄️  Running database setup..."
docker-compose -f docker-compose.prod.yml exec backend python -c "
import asyncio
from app.database.database import init_db

async def setup():
    await init_db()
    print('Database initialized successfully')

asyncio.run(setup())
"

# Check service status
echo "🔍 Checking production service status..."
docker-compose -f docker-compose.prod.yml ps

# Health checks
echo "🏥 Running health checks..."
sleep 10

services=("backend:8000" "frontend:80")
for service in "${services[@]}"; do
    container=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if docker-compose -f docker-compose.prod.yml exec $container curl -f http://localhost:$port/health &> /dev/null; then
        echo "✅ $container is healthy"
    else
        echo "❌ $container health check failed"
    fi
done

# Setup log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/mood-diary > /dev/null <<EOF
/opt/mood-diary/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        docker-compose -f $PWD/docker-compose.prod.yml restart nginx
    endscript
}
EOF

# Setup automatic backups
echo "💾 Setting up automatic database backups..."
sudo tee /etc/cron.d/mood-diary-backup > /dev/null <<EOF
# Backup database daily at 2 AM
0 2 * * * $USER cd $PWD && docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U \$POSTGRES_USER \$POSTGRES_DB | gzip > /opt/mood-diary/backups/backup_\$(date +\%Y\%m\%d).sql.gz
# Clean old backups (keep 30 days)
0 3 * * * find /opt/mood-diary/backups -name "backup_*.sql.gz" -mtime +30 -delete
EOF

# Setup monitoring alerts (basic)
if command -v systemctl &> /dev/null; then
    echo "📊 Setting up basic monitoring..."
    
    # Create service monitoring script
    sudo tee /usr/local/bin/mood-diary-monitor.sh > /dev/null <<EOF
#!/bin/bash
cd $PWD
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "Some services are down, attempting restart..."
    docker-compose -f docker-compose.prod.yml up -d
    systemctl --user start mood-diary-notify || echo "Notification service not available"
fi
EOF
    
    sudo chmod +x /usr/local/bin/mood-diary-monitor.sh
    
    # Add to crontab (check every 5 minutes)
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/mood-diary-monitor.sh") | crontab -
fi

echo ""
echo "🎉 Production deployment completed successfully!"
echo ""
echo "🌐 Your application should be available at:"
echo "   Frontend: http://localhost (or your domain)"
echo "   Backend API: http://localhost:8000 (internal)"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "📊 Monitoring:"
echo "   Service status: docker-compose -f docker-compose.prod.yml ps"
echo "   All logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Backend logs: docker-compose -f docker-compose.prod.yml logs -f backend"
echo "   Bot logs: docker-compose -f docker-compose.prod.yml logs -f telegram_bot"
echo ""
echo "💾 Backups:"
echo "   Location: /opt/mood-diary/backups/"
echo "   Schedule: Daily at 2 AM"
echo "   Manual backup: docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U \$POSTGRES_USER \$POSTGRES_DB > backup.sql"
echo ""
echo "🔧 Management:"
echo "   Stop: docker-compose -f docker-compose.prod.yml down"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
echo "   Update: git pull && ./deploy-prod.sh"
echo ""
echo "🔒 Security recommendations:"
echo "   - Setup SSL certificates"
echo "   - Configure firewall (UFW recommended)"
echo "   - Enable fail2ban"
echo "   - Regular security updates"
echo "   - Monitor logs for suspicious activity"
echo ""
echo "✅ Production deployment is ready!"