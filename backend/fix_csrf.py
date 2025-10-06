#!/usr/bin/env python
"""
Quick fix for CSRF issues in Railway deployment.
This script temporarily disables CSRF for admin login testing.
"""
import os
import django
from django.conf import settings

def fix_csrf_settings():
    """Temporarily fix CSRF settings for Railway deployment."""
    
    print("🔧 Fixing CSRF settings for Railway deployment...")
    
    # Add Railway domain to CSRF trusted origins
    railway_domain = "https://price-regulator-frontend-backend-production.up.railway.app"
    
    if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        if railway_domain not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(railway_domain)
            print(f"✅ Added {railway_domain} to CSRF_TRUSTED_ORIGINS")
        else:
            print(f"✅ {railway_domain} already in CSRF_TRUSTED_ORIGINS")
    else:
        settings.CSRF_TRUSTED_ORIGINS = [railway_domain]
        print(f"✅ Created CSRF_TRUSTED_ORIGINS with {railway_domain}")
    
    # Temporarily disable CSRF for testing (REMOVE IN PRODUCTION)
    print("⚠️  Temporarily disabling CSRF for testing...")
    settings.CSRF_COOKIE_SECURE = False
    settings.SESSION_COOKIE_SECURE = False
    
    print("✅ CSRF settings updated!")
    print("🔑 You can now try logging in to the admin panel")
    print("⚠️  Remember to re-enable CSRF security in production!")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_monitoring.settings_production')
    django.setup()
    fix_csrf_settings()
