# 🌟 Your Neon Database Setup Guide

This guide is specifically configured for your Neon database connection.

## 📋 Your Database Details
- **Host**: `ep-divine-art-adw2ivpe-pooler.c-2.us-east-1.aws.neon.tech`
- **Database**: `neondb`
- **Username**: `neondb_owner`
- **Password**: `npg_iZGzN6wpy8td`
- **Port**: `5432`
- **SSL**: Required

## 🚀 Quick Setup (Recommended)

### Step 1: Create Environment File
```bash
# Copy the example file
cp backend/env.example backend/.env
```

### Step 2: Verify .env File
Your `backend/.env` file should contain:
```env
SECRET_KEY=django-insecure-change-me-in-production-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database - Your Neon Configuration
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_iZGzN6wpy8td
DB_HOST=ep-divine-art-adw2ivpe-pooler.c-2.us-east-1.aws.neon.tech
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Step 3: Test Database Connection
```bash
# Install psycopg2 if not already installed
pip install psycopg2-binary

# Test the connection
python test-neon-connection.py
```

### Step 4: Run with Docker (Recommended)
```bash
# Use the Neon-specific Docker Compose
docker-compose -f docker-compose.neon.yml up -d --build

# Run migrations
docker-compose -f docker-compose.neon.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.neon.yml exec backend python manage.py createsuperuser

# Create demo users
docker-compose -f docker-compose.neon.yml exec backend python manage.py create_demo_users

# Create demo data
docker-compose -f docker-compose.neon.yml exec backend python manage.py create_demo_data
```

## 🛠️ Manual Setup (Without Docker)

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Test connection
python ../test-neon-connection.py

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create demo users
python manage.py create_demo_users

# Create demo data
python manage.py create_demo_data

# Start Django server
python manage.py runserver
```

### Start Celery (Terminal 2)
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Start Celery worker
celery -A price_monitoring worker --loglevel=info
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp env.local.example .env.local

# Start development server
npm run dev
```

## 🔧 Verification Steps

### 1. Test Database Connection
```bash
python test-neon-connection.py
```
Expected output:
```
🔍 Testing Neon database connection...
Host: ep-divine-art-adw2ivpe-pooler.c-2.us-east-1.aws.neon.tech
Database: neondb
User: neondb_owner
Port: 5432

✅ Connection successful!
📊 PostgreSQL version: PostgreSQL 15.x
📊 Current database: neondb
📊 Current user: neondb_owner
✅ All tests passed! Your Neon database is ready to use.
```

### 2. Check Django Connection
```bash
cd backend
python manage.py dbshell
```
You should see a PostgreSQL prompt. Type `\q` to exit.

### 3. Verify Services
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000/api
- **Admin**: http://localhost:8000/admin

### 4. Login with Demo Users
- **Admin**: admin@example.com / admin123
- **Investigator**: investigator@example.com / investigator123
- **Regulator**: regulator@example.com / regulator123

## 🚨 Troubleshooting

### Connection Issues
```bash
# Test connection manually
python test-neon-connection.py

# Check if psycopg2 is installed
pip install psycopg2-binary

# Verify .env file exists and has correct values
cat backend/.env
```

### Docker Issues
```bash
# Check if services are running
docker-compose -f docker-compose.neon.yml ps

# View logs
docker-compose -f docker-compose.neon.yml logs -f backend

# Restart services
docker-compose -f docker-compose.neon.yml restart
```

### Migration Issues
```bash
# Check database connection
python manage.py dbshell

# Run migrations manually
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## 🎯 Success Indicators

You'll know everything is working when:
- ✅ **Database connection test** passes
- ✅ **Django migrations** run successfully
- ✅ **Admin panel** loads at /admin
- ✅ **Demo users** can login
- ✅ **API endpoints** respond correctly
- ✅ **Frontend** connects to backend

## 📊 Your Database Features

With your Neon database, you get:
- ✅ **Serverless PostgreSQL** - No server management
- ✅ **Automatic scaling** - Handles traffic spikes
- ✅ **Built-in backups** - Data protection
- ✅ **SSL encryption** - Secure connections
- ✅ **Connection pooling** - Better performance
- ✅ **Global availability** - Fast worldwide access

## 🎉 Ready to Go!

Your Price Regulation Monitoring System is now configured for your specific Neon database. Everything should work seamlessly! 🚀
