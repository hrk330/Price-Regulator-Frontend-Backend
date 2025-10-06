# Railpack Deployment Guide

## 🚀 Deploying to Railpack

### Prerequisites
- Railpack account
- PostgreSQL database (Railway, Neon, or similar)
- Redis instance (for caching and Celery)

### Environment Variables to Set in Railpack

```bash
# Database Configuration
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://your_redis_host:6379/0

# Django Configuration
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=price_monitoring.settings_production

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Deployment Steps

1. **Connect your repository to Railpack**
2. **Set environment variables** in Railpack dashboard
3. **Deploy** - Railpack will automatically:
   - Detect and install Python (if needed)
   - Install Python dependencies
   - Run database migrations
   - Collect static files
   - Create admin user
   - Start the Django server

### Alternative Deployment Methods

#### Option 1: Railpack (Recommended)
- Uses `deploy.sh` script with automatic Python detection
- Handles multiple Linux distributions
- Automatic dependency installation

#### Option 2: Docker
- Uses `Dockerfile` for containerized deployment
- Consistent environment across platforms
- Built-in Python 3.12 installation

#### Option 3: Manual Deployment
- Use `start.sh` for manual server deployment
- Requires Python 3.12+ to be pre-installed

### Post-Deployment

1. **Access your application**: `https://your-app.railpack.app`
2. **Admin panel**: `https://your-app.railpack.app/admin/`
   - Username: `admin@example.com`
   - Password: `admin123`
3. **API documentation**: `https://your-app.railpack.app/api/docs/`

### Features Available After Deployment

- ✅ **PDF Rate List Import**: Upload government rate lists and automatically extract products
- ✅ **Web Scraping**: Monitor prices from various websites
- ✅ **Violation Detection**: Automatically detect price violations
- ✅ **Admin Interface**: Manage products, cases, and reports
- ✅ **API Endpoints**: Full REST API for frontend integration

### Database Setup

The deployment script will automatically:
- Run all Django migrations
- Create necessary database tables
- Set up initial admin user

### Monitoring

- Check logs in Railpack dashboard
- Monitor database connections
- Verify Redis connectivity for caching

### Troubleshooting

1. **Database connection issues**: Verify environment variables
2. **Static files not loading**: Check `STATIC_ROOT` configuration
3. **Redis connection issues**: Verify `REDIS_URL` format
4. **Admin user not created**: Check logs for user creation errors
5. **`ModuleNotFoundError: No module named 'pkg_resources'`**:
   - This is fixed by adding `setuptools>=65.0.0` to requirements.txt
   - The deployment scripts now install setuptools first
   - If still occurring, run: `pip install --upgrade setuptools wheel`
6. **Python command not found**: Use the `deploy.sh` script which auto-detects Python

### Scaling

- **Horizontal scaling**: Railpack supports multiple instances
- **Database**: Use connection pooling for better performance
- **Caching**: Redis caching is already configured
- **Background tasks**: Celery workers for scraping jobs
