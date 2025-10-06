#!/usr/bin/env python
"""
Check the status of scraping jobs to verify they're being updated correctly.
"""
import os
import django
from django.conf import settings

def check_job_status():
    """Check the status of recent scraping jobs."""
    
    print("🔍 Checking Scraping Job Status")
    print("=" * 50)
    
    from apps.scraping.models import ScrapingJob, ScrapedProduct
    
    # Get recent jobs
    recent_jobs = ScrapingJob.objects.all().order_by('-created_at')[:5]
    
    print(f"📋 Found {recent_jobs.count()} recent jobs:")
    print()
    
    for job in recent_jobs:
        print(f"🆔 Job ID: {job.id}")
        print(f"📝 Name: {job.name}")
        print(f"📊 Status: {job.status}")
        print(f"⏰ Created: {job.created_at}")
        print(f"⏱️  Started: {job.started_at}")
        print(f"✅ Completed: {job.completed_at}")
        print(f"📈 Products Scraped: {job.products_scraped}")
        print(f"🔍 Products Found: {job.products_found}")
        print(f"❌ Errors: {job.errors_count}")
        print(f"📝 Current Progress: {job.current_progress}")
        
        # Count actual scraped products
        scraped_count = ScrapedProduct.objects.filter(scraping_job=job).count()
        print(f"💾 Actual Scraped Products in DB: {scraped_count}")
        
        # Show recent logs
        logs = job.logs.all().order_by('-timestamp')[:3]
        if logs:
            print("📋 Recent Logs:")
            for log in logs:
                print(f"   [{log.level.upper()}] {log.message}")
        
        print("-" * 30)
        print()
    
    # Show total scraped products
    total_products = ScrapedProduct.objects.count()
    print(f"📊 Total Scraped Products in Database: {total_products}")
    
    if total_products > 0:
        print("✅ Scraping is working! Products are being saved to the database.")
    else:
        print("❌ No products found in database. There might be an issue.")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_monitoring.settings_production')
    django.setup()
    check_job_status()
