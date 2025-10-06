#!/bin/bash

# Price Regulation Monitoring System - Universal Deployment Script
echo "🚀 Starting Price Regulation Monitoring System Deployment..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect the environment and install Python if needed
echo "🔍 Detecting environment..."

# Check for different package managers and install Python
if command_exists apt-get; then
    echo "📦 Detected apt-get (Ubuntu/Debian)"
    if ! command_exists python3; then
        echo "Installing Python3..."
        apt-get update
        apt-get install -y python3 python3-pip python3-venv python3-dev
    fi
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command_exists yum; then
    echo "📦 Detected yum (CentOS/RHEL)"
    if ! command_exists python3; then
        echo "Installing Python3..."
        yum install -y python3 python3-pip python3-devel
    fi
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command_exists apk; then
    echo "📦 Detected apk (Alpine)"
    if ! command_exists python3; then
        echo "Installing Python3..."
        apk add --no-cache python3 py3-pip python3-dev
    fi
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command_exists brew; then
    echo "📦 Detected brew (macOS)"
    if ! command_exists python3; then
        echo "Installing Python3..."
        brew install python3
    fi
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    echo "⚠️ No package manager detected, trying to use existing Python..."
    if command_exists python3; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif command_exists python; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        echo "❌ No Python installation found!"
        exit 1
    fi
fi

echo "✅ Using Python command: $PYTHON_CMD"
echo "✅ Using pip command: $PIP_CMD"

# Verify Python installation
$PYTHON_CMD --version || {
    echo "❌ Python installation failed!"
    exit 1
}

# Set production settings
export DJANGO_SETTINGS_MODULE=price_monitoring.settings_production

# Navigate to backend directory
cd backend || {
    echo "❌ Backend directory not found!"
    exit 1
}

# Install Python dependencies
echo "📦 Installing Python dependencies..."
$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements.txt || {
    echo "❌ Failed to install dependencies!"
    exit 1
}

# Run database migrations
echo "🗄️ Running database migrations..."
$PYTHON_CMD manage.py migrate || {
    echo "❌ Database migration failed!"
    exit 1
}

# Collect static files
echo "📁 Collecting static files..."
$PYTHON_CMD manage.py collectstatic --noinput || {
    echo "⚠️ Static files collection failed, continuing..."
}

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
" || {
    echo "⚠️ Superuser creation failed, continuing..."
}

# Start the Django server
echo "🌐 Starting Django server..."
$PYTHON_CMD manage.py runserver 0.0.0.0:${PORT:-8000}
