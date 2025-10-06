#!/bin/bash

# Price Regulation Monitoring System - Neon Database Setup Script

echo "🌟 Setting up Price Regulation Monitoring System with Neon Database..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env file..."
    cp backend/env.example backend/.env
    echo "✅ Created backend/.env from template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit backend/.env file with your Neon database credentials:"
    echo "   - DB_NAME=neondb"
    echo "   - DB_USER=neondb_owner"
    echo "   - DB_PASSWORD=npg_iZGzN6wpy8td"
    echo "   - DB_HOST=ep-divine-art-adw2ivpe-pooler.c-2.us-east-1.aws.neon.tech"
    echo "   - DB_PORT=5432"
    echo ""
    echo "Press Enter after updating the .env file..."
    read
else
    echo "ℹ️  backend/.env already exists"
fi

# Check if frontend .env.local exists
if [ ! -f frontend/.env.local ]; then
    cp frontend/env.local.example frontend/.env.local
    echo "✅ Created frontend/.env.local from template"
else
    echo "ℹ️  frontend/.env.local already exists"
fi

# Test Neon connection
echo "🔍 Testing Neon database connection..."
cd backend
python -c "
import os
from decouple import config
import psycopg2

try:
    conn = psycopg2.connect(
        host=config('DB_HOST'),
        database=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        port=config('DB_PORT', default=5432),
        sslmode='require'
    )
    print('✅ Neon database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Neon database connection failed: {e}')
    print('Please check your .env file configuration.')
    exit(1)
"
cd ..

if [ $? -ne 0 ]; then
    echo "❌ Database connection test failed. Please check your Neon credentials."
    exit 1
fi

# Build and start services (without local PostgreSQL)
echo "🐳 Building and starting services with Neon database..."
docker-compose -f docker-compose.neon.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️  Running database migrations on Neon..."
docker-compose -f docker-compose.neon.yml exec backend python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
echo "You'll be prompted to create a superuser account."
docker-compose -f docker-compose.neon.yml exec backend python manage.py createsuperuser

# Create demo users
echo "👥 Creating demo users..."
docker-compose -f docker-compose.neon.yml exec backend python manage.py create_demo_users

# Create demo data
echo "📊 Creating demo data..."
docker-compose -f docker-compose.neon.yml exec backend python manage.py create_demo_data

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.neon.yml exec backend python manage.py collectstatic --noinput

echo ""
echo "🎉 Setup completed successfully with Neon Database!"
echo ""
echo "📋 Access Information:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/api"
echo "   Admin Panel: http://localhost:8000/admin"
echo ""
echo "👤 Demo Users:"
echo "   Admin: admin@example.com / admin123"
echo "   Investigator: investigator@example.com / investigator123"
echo "   Regulator: regulator@example.com / regulator123"
echo ""
echo "🌟 Database: Neon (Cloud PostgreSQL)"
echo "   - Serverless and scalable"
echo "   - Automatic backups"
echo "   - SSL encrypted connections"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs: docker-compose -f docker-compose.neon.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.neon.yml down"
echo "   Restart services: docker-compose -f docker-compose.neon.yml restart"
echo ""
echo "Happy monitoring with Neon! 🚀"
