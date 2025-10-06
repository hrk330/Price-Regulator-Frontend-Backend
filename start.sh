#!/bin/bash

# Price Regulation Monitoring System - Railpack Deployment Script
echo "🚀 Starting Price Regulation Monitoring System..."

# Set production settings
export DJANGO_SETTINGS_MODULE=price_monitoring.settings_production

# Navigate to backend directory
cd backend

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell -c "
from apps.accounts.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('✅ Superuser created: admin@example.com / admin123')
else:
    print('✅ Superuser already exists')
"

# Start the Django server
echo "🌐 Starting Django server..."
python manage.py runserver 0.0.0.0:${PORT:-8000}
