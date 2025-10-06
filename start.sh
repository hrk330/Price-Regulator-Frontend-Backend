#!/bin/bash

# Price Regulation Monitoring System - Railpack Deployment Script
echo "🚀 Starting Price Regulation Monitoring System..."

# Check Python installation
echo "🐍 Checking Python installation..."
which python3 || which python || echo "Python not found, installing..."

# Install Python if not available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "📦 Installing Python..."
    apt-get update
    apt-get install -y python3 python3-pip python3-venv
fi

# Set Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo "✅ Using Python command: $PYTHON_CMD"

# Set production settings
export DJANGO_SETTINGS_MODULE=price_monitoring.settings_production

# Navigate to backend directory
cd backend

# Install Python dependencies
echo "📦 Installing Python dependencies..."
$PIP_CMD install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
$PYTHON_CMD manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
$PYTHON_CMD manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
$PYTHON_CMD manage.py shell -c "
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
$PYTHON_CMD manage.py runserver 0.0.0.0:${PORT:-8000}
