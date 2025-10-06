from django.db import models
from django.core.validators import MinValueValidator
import json


class ScrapingWebsite(models.Model):
    """Configuration for websites to scrape."""
    
    name = models.CharField(max_length=255)
    base_url = models.URLField(max_length=500)
    search_url_template = models.CharField(max_length=500, help_text="URL template with {query} placeholder")
    is_active = models.BooleanField(default=True)
    scraping_config = models.JSONField(default=dict, help_text="CSS selectors and parsing rules")
    rate_limit_delay = models.FloatField(default=1.0, help_text="Delay between requests in seconds")
    headers = models.JSONField(default=dict, help_text="Custom headers for requests")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.base_url}"


class ProductSearchList(models.Model):
    """List of products that admin wants to search for on websites."""
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    products = models.JSONField(default=list, help_text="List of product names to search")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({len(self.products)} products)"


class ScrapedProduct(models.Model):
    """Products scraped from ecommerce sites."""
    
    MARKETPLACE_CHOICES = [
        ('amazon', 'Amazon'),
        ('ebay', 'eBay'),
        ('walmart', 'Walmart'),
        ('target', 'Target'),
        ('other', 'Other'),
    ]
    
    product_name = models.CharField(max_length=255)
    marketplace = models.CharField(max_length=50, choices=MARKETPLACE_CHOICES)
    website = models.ForeignKey(ScrapingWebsite, on_delete=models.CASCADE, null=True, blank=True)
    search_query = models.CharField(max_length=255, help_text="Original search query used")
    listed_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, blank=True,
        help_text="Original price before any discounts"
    )
    url = models.URLField(max_length=500)
    image_url = models.URLField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    availability = models.BooleanField(default=True)
    stock_status = models.CharField(max_length=100, blank=True)
    seller_name = models.CharField(max_length=255, blank=True)
    rating = models.FloatField(null=True, blank=True)
    review_count = models.IntegerField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    scraping_job = models.ForeignKey('ScrapingJob', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['marketplace', 'scraped_at']),
            models.Index(fields=['product_name', 'marketplace']),
        ]
    
    def __str__(self):
        return f"{self.product_name} - {self.marketplace} - ${self.listed_price}"


class ScrapingJob(models.Model):
    """Track scraping jobs and their status."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=255)
    website = models.ForeignKey(ScrapingWebsite, on_delete=models.CASCADE)
    product_list = models.ForeignKey(ProductSearchList, on_delete=models.CASCADE, null=True, blank=True)
    marketplace = models.CharField(max_length=50, choices=ScrapedProduct.MARKETPLACE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    products_scraped = models.IntegerField(default=0)
    products_found = models.IntegerField(default=0)
    errors_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    task_id = models.CharField(max_length=255, blank=True, help_text="Celery task ID")
    scheduled_at = models.DateTimeField(null=True, blank=True, help_text="When to start the scraping job")
    auto_start = models.BooleanField(default=True, help_text="Automatically start job when created")
    current_progress = models.TextField(blank=True, help_text="Current progress message")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.status}"


class ScrapingJobLog(models.Model):
    """Store real-time logs for scraping jobs."""
    
    LOG_LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]
    
    job = models.ForeignKey(ScrapingJob, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, default='info')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.job.name} - {self.level}: {self.message[:50]}"
