#!/bin/bash
set -e

echo "🚀 Starting Price Regulation Monitoring System..."

# Ensure setuptools is available
echo "🔧 Ensuring setuptools is available..."
pip install --upgrade setuptools wheel || echo "⚠️ Could not upgrade setuptools, continuing..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! python manage.py check --database default 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "✅ Database is ready!"

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
