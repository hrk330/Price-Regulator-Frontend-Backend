# 🌟 Neon Database Setup Guide

Complete guide to configure the Price Regulation Monitoring System with Neon Database.

## 🎯 What is Neon?
- **Serverless PostgreSQL** in the cloud
- **Free tier** with 0.5GB storage
- **Automatic scaling** and backups
- **Built-in connection pooling**
- **Perfect for Django projects**

## 📋 Step 1: Create Neon Database

### 1.1 Sign up for Neon
1. Go to: https://neon.tech/
2. Click "Sign Up" and create an account
3. Create a new project

### 1.2 Get Connection Details
From your Neon dashboard, copy these details:
- **Host**: `ep-xxx-xxx.us-east-1.aws.neon.tech`
- **Database**: `neondb` (or your custom name)
- **Username**: `neondb_owner`
- **Password**: `your_generated_password`
- **Port**: `5432`

## ⚙️ Step 2: Configure Backend

### 2.1 Create Environment File
```bash
# Copy the example file
cp backend/env.example backend/.env

# Edit backend/.env with your Neon credentials
```

### 2.2 Update .env File
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Neon Database Configuration
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=your_neon_password_here
DB_HOST=ep-xxx-xxx.us-east-1.aws.neon.tech
DB_PORT=5432

# Redis (still needed for Celery)
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 🐳 Step 3: Docker Setup (Recommended)

### 3.1 Use Neon-Specific Docker Compose
```bash
# Make setup script executable
chmod +x setup-neon.sh

# Run the setup script
./setup-neon.sh
```

### 3.2 Manual Docker Commands
```bash
# Build and start services
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

## 🛠️ Step 4: Manual Setup (Without Docker)

### 4.1 Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Test Neon connection
python -c "
import psycopg2
from decouple import config

conn = psycopg2.connect(
    host=config('DB_HOST'),
    database=config('DB_NAME'),
    user=config('DB_USER'),
    password=config('DB_PASSWORD'),
    port=config('DB_PORT'),
    sslmode='require'
)
print('✅ Neon connection successful!')
conn.close()
"

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

### 4.2 Start Celery (Terminal 2)
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Start Celery worker
celery -A price_monitoring worker --loglevel=info
```

### 4.3 Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp env.local.example .env.local

# Start development server
npm run dev
```

## 🔧 Step 5: Verify Setup

### 5.1 Test Database Connection
```bash
# Test from backend directory
python manage.py dbshell

# You should see PostgreSQL prompt
# Type \q to exit
```

### 5.2 Check Services
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000/api
- **Admin**: http://localhost:8000/admin

### 5.3 Login with Demo Users
- **Admin**: admin@example.com / admin123
- **Investigator**: investigator@example.com / investigator123
- **Regulator**: regulator@example.com / regulator123

## 🚨 Troubleshooting

### Common Issues

#### 1. SSL Connection Error
```bash
# Ensure sslmode=require in database config
# Check if your Neon project has SSL enabled
```

#### 2. Connection Timeout
```bash
# Check your Neon host URL
# Verify firewall settings
# Ensure port 5432 is accessible
```

#### 3. Authentication Failed
```bash
# Double-check username and password
# Ensure user has proper permissions
# Check if password contains special characters
```

#### 4. Database Not Found
```bash
# Verify database name in Neon dashboard
# Check if database exists in your Neon project
```

## 🌟 Neon Benefits

### Why Neon is Great for This Project:
- ✅ **Serverless**: No server management
- ✅ **Automatic Scaling**: Handles traffic spikes
- ✅ **Built-in Backups**: Data protection
- ✅ **Connection Pooling**: Better performance
- ✅ **Free Tier**: Perfect for development
- ✅ **SSL Security**: Encrypted connections
- ✅ **Global Availability**: Fast worldwide access

## 📊 Monitoring

### Neon Dashboard Features:
- **Connection monitoring**
- **Query performance**
- **Storage usage**
- **Backup history**
- **Connection logs**

## 🔄 Production Deployment

### For Production:
1. **Upgrade Neon plan** for production use
2. **Set up monitoring** and alerts
3. **Configure backups** schedule
4. **Set up connection pooling**
5. **Monitor performance** metrics

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ **Neon connection** test passes
- ✅ **Django migrations** run successfully
- ✅ **Admin panel** loads at /admin
- ✅ **Demo users** can login
- ✅ **API endpoints** respond correctly
- ✅ **Frontend** connects to backend

## 🆘 Support

### Neon Support:
- **Documentation**: https://neon.tech/docs
- **Community**: https://neon.tech/community
- **Support**: Available in Neon dashboard

### Project Support:
- Check logs: `docker-compose -f docker-compose.neon.yml logs -f`
- Verify environment variables
- Test database connection manually

---

**🎯 Your Price Regulation Monitoring System is now powered by Neon Database!** 🚀
