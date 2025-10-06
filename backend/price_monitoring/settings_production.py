"""
Production settings for Price Regulation Monitoring System.
"""
import os
from .settings import *

# Security settings for production
DEBUG = False
ALLOWED_HOSTS = ['*']  # Configure with your actual domain

# Database configuration for production
# Check if we have database environment variables
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT', '5432')

# If no database is configured, use SQLite for development/testing
if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST]):
    print("⚠️  No database environment variables found. Using SQLite for development.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    print(f"✅ Using PostgreSQL database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
            'OPTIONS': {
                'sslmode': 'require' if DB_HOST != 'localhost' else 'prefer',
            },
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
        }
    }

# Redis configuration for production
REDIS_URL = os.environ.get('REDIS_URL')

# If no Redis is configured, use local memory cache
if not REDIS_URL:
    print("⚠️  No Redis URL found. Using local memory cache.")
    REDIS_URL = 'redis://localhost:6379/0'
    
    # Use local memory cache instead of Redis
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': 300,
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake-sessions',
            'TIMEOUT': 86400,
        }
    }
    
    # Use database for Celery when Redis is not available
    CELERY_BROKER_URL = 'db+sqlite:///celery.db'
    CELERY_RESULT_BACKEND = 'db+sqlite:///celery.db'
else:
    print(f"✅ Using Redis: {REDIS_URL}")
    
    # Celery configuration for production
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # Cache configuration for production
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'TIMEOUT': 300,
            'OPTIONS': {}
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL.replace('/0', '/2'),
            'TIMEOUT': 86400,
            'OPTIONS': {}
        }
    }

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",  # Replace with your actual frontend domain
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
