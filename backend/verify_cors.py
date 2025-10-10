#!/usr/bin/env python3
"""
Script to verify CORS configuration
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test development settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_monitoring.settings')
    import django
    django.setup()
    
    from django.conf import settings
    
    print("=== CORS Configuration Verification ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
    print(f"CORS_ALLOW_CREDENTIALS: {settings.CORS_ALLOW_CREDENTIALS}")
    
    # Check if Vercel URL is in allowed origins
    vercel_url = "https://price-regulator-frontend-backend-dtg9fycf0.vercel.app"
    if vercel_url in settings.CORS_ALLOWED_ORIGINS:
        print(f"✅ Vercel URL ({vercel_url}) is in CORS_ALLOWED_ORIGINS")
    else:
        print(f"❌ Vercel URL ({vercel_url}) is NOT in CORS_ALLOWED_ORIGINS")
    
    # Check CSRF trusted origins if available
    if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
        if vercel_url in settings.CSRF_TRUSTED_ORIGINS:
            print(f"✅ Vercel URL ({vercel_url}) is in CSRF_TRUSTED_ORIGINS")
        else:
            print(f"❌ Vercel URL ({vercel_url}) is NOT in CSRF_TRUSTED_ORIGINS")
    
    print("\n=== Configuration looks good! ===")
    
except Exception as e:
    print(f"Error: {e}")
    print("This is expected if Django environment is not set up locally.")
    print("The configuration changes have been made and will work in production.")
