from celery import shared_task
from django.utils import timezone
from decimal import Decimal
from .models import ScrapingJob, ScrapedProduct, ScrapingWebsite, ProductSearchList, ScrapingJobLog
from apps.products.models import RegulatedProduct
from apps.violations.models import Violation, ViolationCheckReport
from .scraping_engines import get_scraping_engine
import logging
import json

logger = logging.getLogger(__name__)


def log_job_progress(job, level, message):
    """Log progress to both database and console."""
    # Log to console
    logger.info(f"Celery: [{level.upper()}] {message}")
    
    # Log to database
    try:
        ScrapingJobLog.objects.create(
            job=job,
            level=level,
            message=message
        )
        # Update current progress
        job.current_progress = message
        job.save(update_fields=['current_progress'])
    except Exception as e:
        logger.error(f"Failed to save log to database: {str(e)}")


@shared_task(bind=True)
def scrape_marketplace(self, job_id):
    """Celery task to scrape products from a marketplace."""
    
    logger.info(f"Celery: Starting scrape_marketplace task for job_id: {job_id}")
    logger.info(f"Celery: Task ID: {self.request.id}")
    
    try:
        job = ScrapingJob.objects.get(id=job_id)
        log_job_progress(job, 'info', f"Task started - Found job: {job.name}")
        
        job.status = 'running'
        job.started_at = timezone.now()
        job.task_id = self.request.id
        job.save()
        log_job_progress(job, 'info', "Job status updated to 'running'")
        
        # Get website configuration
        website = job.website
        log_job_progress(job, 'info', f"Website: {website.name} (active: {website.is_active})")
        
        if not website.is_active:
            raise Exception(f"Website {website.name} is not active")
        
        # Get products to search for
        search_products = []
        if job.product_list and job.product_list.is_active:
            search_products = job.product_list.products
            log_job_progress(job, 'info', f"Using product list '{job.product_list.name}' with {len(search_products)} products")
        else:
            # Fallback to regulated products
            regulated_products = RegulatedProduct.objects.filter(is_active=True)
            search_products = [product.name for product in regulated_products]
            log_job_progress(job, 'info', f"Using regulated products, found {len(search_products)} products")
        
        if not search_products:
            raise Exception("No products to search for")
        
        log_job_progress(job, 'info', f"Products to search: {', '.join(search_products[:3])}...")  # Show first 3 products
        
        # Initialize scraping engine
        website_config = {
            'base_url': website.base_url,
            'search_url_template': website.search_url_template,
            'scraping_config': website.scraping_config,
            'rate_limit_delay': website.rate_limit_delay,
            'headers': website.headers,
            'marketplace': job.marketplace,
            'use_selenium': website.use_selenium,
            'fallback_to_selenium': website.fallback_to_selenium,
            'selenium_config': website.selenium_config
        }
        
        log_job_progress(job, 'info', f"Initializing scraping engine for marketplace: {job.marketplace}")
        scraping_engine = get_scraping_engine(website_config)
        log_job_progress(job, 'info', f"Scraping engine initialized: {type(scraping_engine).__name__}")
        
        products_scraped = 0
        products_found = 0
        errors_count = 0
        
        log_job_progress(job, 'info', f"Starting scraping for {len(search_products)} products")
        
        for i, product_name in enumerate(search_products, 1):
            try:
                log_job_progress(job, 'info', f"[{i}/{len(search_products)}] Searching for: {product_name}")
                
                # Search for products
                scraped_products = scraping_engine.search_products(product_name, max_results=10)
                log_job_progress(job, 'info', f"Found {len(scraped_products)} results for '{product_name}'")
                
                for j, scraped_data in enumerate(scraped_products):
                    try:
                        log_job_progress(job, 'info', f"Processing result {j+1} for '{product_name}': {scraped_data.get('name', 'Unknown')}")
                        
                        # Create scraped product record
                        scraped_product = ScrapedProduct.objects.create(
                            product_name=scraped_data['name'],
                            marketplace=job.marketplace,
                            website=website,
                            search_query=product_name,
                            listed_price=scraped_data['price'],
                            original_price=scraped_data.get('original_price'),
                            url=scraped_data['url'],
                            image_url=scraped_data.get('image_url', ''),
                            description=scraped_data.get('description', ''),
                            availability=scraped_data.get('availability', True),
                            stock_status=scraped_data.get('stock_status', ''),
                            seller_name=scraped_data.get('seller_name', ''),
                            rating=scraped_data.get('rating'),
                            review_count=scraped_data.get('review_count'),
                            scraping_job=job
                        )
                        
                        log_job_progress(job, 'success', f"Saved product: {scraped_product.product_name} - ${scraped_product.listed_price}")
                        
                        # Check for violations
                        check_price_violation_for_product(product_name, scraped_product)
                        
                        products_scraped += 1
                        products_found += 1
                        
                    except Exception as e:
                        log_job_progress(job, 'error', f"Error saving scraped product {scraped_data.get('name', 'Unknown')}: {str(e)}")
                        errors_count += 1
                
                if not scraped_products:
                    log_job_progress(job, 'warning', f"No products found for: {product_name}")
                
            except Exception as e:
                log_job_progress(job, 'error', f"Error scraping product {product_name}: {str(e)}")
                errors_count += 1
        
        # Update job status
        log_job_progress(job, 'info', f"Updating job status to 'completed'")
        job.status = 'completed'
        job.products_scraped = products_scraped
        job.products_found = products_found
        job.errors_count = errors_count
        job.completed_at = timezone.now()
        job.current_progress = f"Completed - Products scraped: {products_scraped}, Found: {products_found}, Errors: {errors_count}"
        job.save()
        
        # Invalidate cache after scraping completes
        from django.core.cache import cache
        cache.delete('full_violation_report')
        cache.delete('violation_stats')
        
        log_job_progress(job, 'success', f"Scraping job completed. Products scraped: {products_scraped}, Found: {products_found}, Errors: {errors_count}")
        
        return f"Scraping completed. Products scraped: {products_scraped}, Found: {products_found}, Errors: {errors_count}"
        
    except ScrapingJob.DoesNotExist:
        logger.error(f"Celery: ScrapingJob with id {job_id} not found")
        return "Job not found"
    except Exception as e:
        logger.error(f"Celery: Scraping job failed: {str(e)}")
        try:
            job = ScrapingJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.current_progress = f"Failed: {str(e)}"
            job.save()
            log_job_progress(job, 'error', f"Job failed: {str(e)}")
        except Exception as save_error:
            logger.error(f"Celery: Failed to update job status: {str(save_error)}")
        raise


def check_price_violation_for_product(product_name, scraped_product):
    """Check if scraped price violates government regulations for a specific product."""
    
    try:
        # Use scraped product name for matching, not the search query
        scraped_product_name = scraped_product.product_name
        
        # Find matching regulated product using scraped product name
        regulated_products = RegulatedProduct.objects.filter(
            name__icontains=scraped_product_name,
            is_active=True
        )
        
        if not regulated_products.exists():
            # Try fuzzy matching against all regulated products
            regulated_products = RegulatedProduct.objects.filter(
                is_active=True
            )
            
            for regulated_product in regulated_products:
                if is_product_match(scraped_product_name, regulated_product.name):
                    logger.info(f"Matched '{scraped_product_name}' with '{regulated_product.name}'")
                    check_single_violation(regulated_product, scraped_product)
                    break
            else:
                logger.info(f"No match found for scraped product: '{scraped_product_name}'")
        else:
            # Check against all matching regulated products
            for regulated_product in regulated_products:
                logger.info(f"Direct match found: '{scraped_product_name}' with '{regulated_product.name}'")
                check_single_violation(regulated_product, scraped_product)
                
    except Exception as e:
        logger.error(f"Error checking violations for {scraped_product_name}: {str(e)}")


def is_product_match(search_name, regulated_name):
    """Check if two product names are similar enough to be considered a match."""
    import difflib
    import re
    
    def extract_keywords(name):
        """Extract meaningful keywords from product name."""
        # Remove common words and extract key terms
        name = name.lower().strip()
        
        # Remove common words that don't help with matching
        stop_words = ['the', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'kg', 'liter', 'l', 'piece', 'pcs', 'pack', 'bag', 'box']
        
        # Split by common separators and clean
        words = re.split(r'[\s\-_\(\)\[\]\/]+', name)
        keywords = [word for word in words if word and word not in stop_words and len(word) > 2]
        
        return keywords
    
    def normalize_for_matching(name):
        """Normalize product name for better matching."""
        name = name.lower().strip()
        
        # Remove common variations
        name = re.sub(r'\d+kg', '', name)  # Remove weight specifications
        name = re.sub(r'\d+liter?', '', name)  # Remove volume specifications
        name = re.sub(r'\d+pc?s?', '', name)  # Remove piece specifications
        name = re.sub(r'[\(\)\[\]]', '', name)  # Remove brackets
        name = re.sub(r'\s+', ' ', name)  # Normalize spaces
        
        return name.strip()
    
    # Normalize names
    search_normalized = normalize_for_matching(search_name)
    regulated_normalized = normalize_for_matching(regulated_name)
    
    # Check for exact match
    if search_normalized == regulated_normalized:
        return True
    
    # Check for substring match
    if search_normalized in regulated_normalized or regulated_normalized in search_normalized:
        return True
    
    # Extract keywords and check for keyword overlap
    search_keywords = extract_keywords(search_name)
    regulated_keywords = extract_keywords(regulated_name)
    
    # Check if any significant keywords match
    keyword_matches = 0
    for search_kw in search_keywords:
        for reg_kw in regulated_keywords:
            if search_kw in reg_kw or reg_kw in search_kw:
                keyword_matches += 1
                break
    
    # If we have keyword matches, it's likely a match
    if keyword_matches > 0 and len(search_keywords) > 0:
        match_ratio = keyword_matches / len(search_keywords)
        if match_ratio >= 0.5:  # At least 50% of keywords match
            return True
    
    # Check similarity ratio as fallback
    similarity = difflib.SequenceMatcher(None, search_normalized, regulated_normalized).ratio()
    return similarity > 0.6  # Lowered threshold for better matching


def check_single_violation(regulated_product, scraped_product):
    """Check violation for a single regulated product against scraped product."""
    
    violation_threshold = regulated_product.price_violation_threshold
    scraped_price = scraped_product.listed_price
    regulated_price = regulated_product.gov_price
    
    # Calculate differences
    price_difference = scraped_price - regulated_price
    percentage_difference = (price_difference / regulated_price) * 100 if regulated_price > 0 else 0
    
    # Determine compliance status
    has_violation = scraped_price > violation_threshold
    compliance_status = 'violation' if has_violation else 'ok'
    
    # Calculate severity and penalty if violation
    violation_severity = None
    proposed_penalty = None
    
    if has_violation:
        if percentage_difference <= 20:
            violation_severity = 'low'
            proposed_penalty = Decimal('100')
        elif percentage_difference <= 50:
            violation_severity = 'medium'
            proposed_penalty = Decimal('500')
        elif percentage_difference <= 100:
            violation_severity = 'high'
            proposed_penalty = Decimal('1000')
        else:
            violation_severity = 'critical'
            proposed_penalty = Decimal('2000')
    
    # Create notes
    notes = f"Scraped: Rs.{scraped_price} | Regulated: Rs.{regulated_price} | "
    notes += f"Difference: Rs.{price_difference} ({percentage_difference:.1f}%)"
    
    if has_violation:
        notes += f" | Severity: {violation_severity} | Penalty: Rs.{proposed_penalty}"
    
    # Create or update violation check report
    report, report_created = ViolationCheckReport.objects.get_or_create(
        regulated_product=regulated_product,
        scraped_product=scraped_product,
        defaults={
            'has_violation': has_violation,
            'compliance_status': compliance_status,
            'price_difference': price_difference,
            'percentage_difference': Decimal(str(round(percentage_difference, 2))),
            'violation_severity': violation_severity,
            'proposed_penalty': proposed_penalty,
            'notes': notes,
        }
    )
    
    # Create violation record if needed
    violation_record = None
    if has_violation:
        existing_violation = Violation.objects.filter(
            regulated_product=regulated_product,
            scraped_product=scraped_product,
            status='pending'
        ).first()
        
        if not existing_violation:
            # Create violation
            violation_record = Violation.objects.create(
                regulated_product=regulated_product,
                scraped_product=scraped_product,
                violation_type='price_exceeded',
                severity=violation_severity,
                proposed_penalty=proposed_penalty,
                status='pending',
                notes=notes
            )
            
            logger.info(f"Created violation: {regulated_product.name} - {violation_severity} severity")
        else:
            violation_record = existing_violation
        
        # Link violation record to report
        if violation_record and not report.violation_record:
            report.violation_record = violation_record
            report.save()


@shared_task
def cleanup_old_scraped_products(days_old=30):
    """Clean up old scraped products to manage database size."""
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days_old)
    old_products = ScrapedProduct.objects.filter(scraped_at__lt=cutoff_date)
    
    count = old_products.count()
    old_products.delete()
    
    logger.info(f"Cleaned up {count} old scraped products")
    return f"Cleaned up {count} old scraped products"
