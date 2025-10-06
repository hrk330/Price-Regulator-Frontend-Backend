#!/bin/bash
set -e

echo "🚀 Starting Price Regulation Monitoring System..."

# Ensure setuptools is available
echo "🔧 Ensuring setuptools is available..."
pip install --upgrade setuptools wheel || echo "⚠️ Could not upgrade setuptools, continuing..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
  if python manage.py check --database default 2>/dev/null; then
    echo "✅ Database is ready!"
    break
  else
    echo "Database is unavailable - sleeping (attempt $((attempt + 1))/$max_attempts)"
    sleep 2
    attempt=$((attempt + 1))
  fi
done

if [ $attempt -eq $max_attempts ]; then
  echo "❌ Database connection failed after $max_attempts attempts"
  echo "🔧 This might be because:"
  echo "   1. Database environment variables are not set"
  echo "   2. Database server is not running"
  echo "   3. Network connectivity issues"
  echo ""
  echo "📋 Current environment variables:"
  echo "   DB_NAME: ${DB_NAME:-'not set'}"
  echo "   DB_USER: ${DB_USER:-'not set'}"
  echo "   DB_HOST: ${DB_HOST:-'not set'}"
  echo "   DB_PORT: ${DB_PORT:-'not set'}"
  echo ""
  echo "🚀 Continuing with fallback configuration..."
fi

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

# Start the application
echo "🌐 Starting Django server..."
exec "$@"
