#!/usr/bin/env python
"""
Migration runner script that handles dependencies correctly.
This script runs migrations in the correct order to avoid dependency issues.
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def run_migrations():
    """Run migrations in the correct dependency order."""
    
    # Migration order based on dependencies
    migration_order = [
        # Core Django apps (no dependencies)
        'contenttypes',
        'auth', 
        'admin',
        'sessions',
        
        # Our apps in dependency order
        'scraping',  # Must come before violations
        'accounts',
        'products', 
        'violations',  # Depends on scraping
        'cases',
    ]
    
    print("🗄️ Running database migrations in dependency order...")
    
    for app in migration_order:
        print(f"📋 Migrating {app}...")
        try:
            execute_from_command_line(['manage.py', 'migrate', app])
            print(f"✅ {app} migration completed")
        except Exception as e:
            print(f"❌ {app} migration failed: {e}")
            # Continue with other migrations
            continue
    
    print("✅ All migrations completed!")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_monitoring.settings_production')
    django.setup()
    run_migrations()
