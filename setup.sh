#!/bin/bash

# Price Regulation Monitoring System Setup Script

echo "🚀 Setting up Price Regulation Monitoring System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files if they don't exist
echo "📝 Creating environment files..."

if [ ! -f backend/.env ]; then
    cp backend/env.example backend/.env
    echo "✅ Created backend/.env from template"
else
    echo "ℹ️  backend/.env already exists"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/env.local.example frontend/.env.local
    echo "✅ Created frontend/.env.local from template"
else
    echo "ℹ️  frontend/.env.local already exists"
fi

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
echo "You'll be prompted to create a superuser account."
docker-compose exec backend python manage.py createsuperuser

# Create demo users
echo "👥 Creating demo users..."
docker-compose exec backend python manage.py create_demo_users

# Create demo data
echo "📊 Creating demo data..."
docker-compose exec backend python manage.py create_demo_data

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec backend python manage.py collectstatic --noinput

echo ""
echo "🎉 Setup completed successfully!"
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
echo "🔧 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose up -d --build"
echo ""
echo "📚 Documentation:"
echo "   README.md - Setup and usage instructions"
echo "   API_DOCUMENTATION.md - API reference"
echo ""
echo "Happy monitoring! 🎯"
