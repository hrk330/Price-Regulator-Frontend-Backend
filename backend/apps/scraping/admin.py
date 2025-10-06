from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import ScrapedProduct, ScrapingJob, ScrapingWebsite, ProductSearchList, ScrapingJobLog
from .tasks import scrape_marketplace
from celery import current_app
import logging

logger = logging.getLogger(__name__)


class ScrapingJobLogInline(admin.TabularInline):
    """Inline admin for scraping job logs."""
    model = ScrapingJobLog
    extra = 0
    readonly_fields = ['timestamp']
    fields = ['timestamp', 'level', 'message']
    ordering = ['-timestamp']
    max_num = 20  # Limit to 20 most recent logs
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ScrapingWebsite)
class ScrapingWebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'is_active', 'rate_limit_delay', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'base_url']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'base_url', 'is_active')
        }),
        ('Scraping Configuration', {
            'fields': ('search_url_template', 'scraping_config', 'rate_limit_delay', 'headers')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ProductSearchList)
class ProductSearchListAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'products_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def products_count(self, obj):
        return len(obj.products) if obj.products else 0
    products_count.short_description = 'Products Count'


@admin.register(ScrapedProduct)
class ScrapedProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'marketplace', 'website', 'listed_price', 'availability', 'scraped_at']
    list_filter = ['marketplace', 'website', 'availability', 'scraped_at']
    search_fields = ['product_name', 'description', 'search_query']
    readonly_fields = ['scraped_at']
    ordering = ['-scraped_at']
    list_per_page = 50  # Show 50 items per page instead of default 100
    fieldsets = (
        ('Product Information', {
            'fields': ('product_name', 'marketplace', 'website', 'search_query')
        }),
        ('Pricing', {
            'fields': ('listed_price', 'original_price')
        }),
        ('Product Details', {
            'fields': ('url', 'image_url', 'description', 'availability', 'stock_status')
        }),
        ('Additional Info', {
            'fields': ('seller_name', 'rating', 'review_count', 'scraping_job'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('scraped_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(ScrapingJobLog)
class ScrapingJobLogAdmin(admin.ModelAdmin):
    list_display = ['job', 'level', 'message', 'timestamp']
    list_filter = ['level', 'timestamp', 'job__status']
    search_fields = ['message', 'job__name']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    list_per_page = 100  # Show 100 logs per page


@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'marketplace', 'status', 'products_scraped', 'products_found', 'errors_count', 'current_progress', 'scheduled_at', 'created_at', 'action_buttons']
    list_filter = ['status', 'marketplace', 'website', 'auto_start', 'created_at']
    search_fields = ['name', 'error_message', 'current_progress']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'task_id', 'current_progress']
    ordering = ['-created_at']
    actions = ['start_selected_jobs', 'cancel_selected_jobs', 'cleanup_old_data']
    inlines = [ScrapingJobLogInline]
    list_per_page = 25  # Show 25 jobs per page instead of default 100
    
    fieldsets = (
        ('Job Information', {
            'fields': ('name', 'website', 'product_list', 'marketplace', 'created_by')
        }),
        ('Scheduling', {
            'fields': ('auto_start', 'scheduled_at'),
            'description': 'Set when the job should start. Leave empty for immediate start.'
        }),
        ('Status & Progress', {
            'fields': ('status', 'products_scraped', 'products_found', 'errors_count', 'current_progress', 'task_id')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'created_at')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )
    
    def action_buttons(self, obj):
        """Display action buttons for the job."""
        buttons = []
        
        if obj.status in ['pending', 'scheduled']:
            buttons.append(
                f'<a class="button" href="{reverse("admin:scraping_scrapingjob_start", args=[obj.pk])}" '
                f'onclick="return confirm(\'Start this scraping job?\')">Start</a>'
            )
        
        if obj.status == 'running':
            buttons.append(
                f'<a class="button" href="{reverse("admin:scraping_scrapingjob_cancel", args=[obj.pk])}" '
                f'onclick="return confirm(\'Cancel this scraping job?\')" style="color: red;">Cancel</a>'
            )
        
        return format_html(' '.join(buttons)) if buttons else '-'
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True
    
    def start_selected_jobs(self, request, queryset):
        """Admin action to start selected jobs."""
        started_count = 0
        for job in queryset.filter(status__in=['pending', 'scheduled']):
            if self._start_scraping_job(job):
                started_count += 1
        
        if started_count > 0:
            self.message_user(request, f'Successfully started {started_count} scraping job(s).')
        else:
            self.message_user(request, 'No jobs were started. Only pending/scheduled jobs can be started.', level=messages.WARNING)
    start_selected_jobs.short_description = "Start selected scraping jobs"
    
    def cancel_selected_jobs(self, request, queryset):
        """Admin action to cancel selected jobs."""
        cancelled_count = 0
        for job in queryset.filter(status='running'):
            if self._cancel_scraping_job(job):
                cancelled_count += 1
        
        if cancelled_count > 0:
            self.message_user(request, f'Successfully cancelled {cancelled_count} scraping job(s).')
        else:
            self.message_user(request, 'No jobs were cancelled. Only running jobs can be cancelled.', level=messages.WARNING)
    
    def cleanup_old_data(self, request, queryset):
        """Admin action to cleanup old data."""
        from datetime import datetime, timedelta
        
        # Delete logs older than 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        old_logs = ScrapingJobLog.objects.filter(timestamp__lt=cutoff_date)
        logs_count = old_logs.count()
        old_logs.delete()
        
        # Delete scraped products older than 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        old_products = ScrapedProduct.objects.filter(scraped_at__lt=cutoff_date)
        products_count = old_products.count()
        old_products.delete()
        
        self.message_user(request, f'Cleanup completed: {logs_count} old logs and {products_count} old products deleted.')
    cleanup_old_data.short_description = "Cleanup old data (logs >7 days, products >30 days)"
    cancel_selected_jobs.short_description = "Cancel selected scraping jobs"
    
    def save_model(self, request, obj, form, change):
        """Override save to automatically start job if auto_start is enabled."""
        logger.info(f"Admin: Saving scraping job '{obj.name}' (ID: {obj.id if obj.id else 'new'})")
        logger.info(f"Admin: Auto start: {obj.auto_start}, Status: {obj.status}, Scheduled at: {obj.scheduled_at}")
        
        super().save_model(request, obj, form, change)
        
        # Auto-start the job if conditions are met
        if obj.auto_start and obj.status == 'pending':
            logger.info(f"Admin: Attempting to auto-start job {obj.id}")
            
            if obj.scheduled_at and obj.scheduled_at > timezone.now():
                # Schedule for later
                logger.info(f"Admin: Scheduling job {obj.id} for {obj.scheduled_at}")
                obj.status = 'scheduled'
                obj.save()
                if self._schedule_scraping_job(obj):
                    self.message_user(request, f'Scraping job scheduled for {obj.scheduled_at}.')
                    logger.info(f"Admin: Job {obj.id} scheduled successfully")
                else:
                    self.message_user(request, 'Failed to schedule scraping job.', level=messages.ERROR)
                    logger.error(f"Admin: Failed to schedule job {obj.id}")
            else:
                # Start immediately
                logger.info(f"Admin: Starting job {obj.id} immediately")
                if self._start_scraping_job(obj):
                    self.message_user(request, 'Scraping job started successfully.')
                    logger.info(f"Admin: Job {obj.id} started successfully")
                else:
                    self.message_user(request, 'Failed to start scraping job.', level=messages.ERROR)
                    logger.error(f"Admin: Failed to start job {obj.id}")
        else:
            logger.info(f"Admin: Job {obj.id} not auto-started (auto_start: {obj.auto_start}, status: {obj.status})")
    
    def _start_scraping_job(self, job):
        """Start a scraping job."""
        logger.info(f"Admin: Starting scraping job {job.id} - {job.name}")
        
        try:
            # Validate job data
            logger.info(f"Admin: Job validation - Website: {job.website.name}, Product list: {job.product_list.name if job.product_list else 'None'}")
            
            if not job.website.is_active:
                raise Exception(f"Website {job.website.name} is not active")
            
            if job.product_list and not job.product_list.is_active:
                raise Exception(f"Product list {job.product_list.name} is not active")
            
            # Update job status
            logger.info(f"Admin: Updating job {job.id} status to 'running'")
            job.status = 'running'
            job.started_at = timezone.now()
            job.save()
            
            # Start the Celery task
            logger.info(f"Admin: Calling Celery task scrape_marketplace.delay({job.id})")
            task = scrape_marketplace.delay(job.id)
            logger.info(f"Admin: Celery task created with ID: {task.id}")
            
            # Save task ID
            job.task_id = task.id
            job.save()
            logger.info(f"Admin: Job {job.id} started successfully with task ID {task.id}")
            
            return True
        except Exception as e:
            logger.error(f"Admin: Failed to start job {job.id}: {str(e)}")
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            return False
    
    def _cancel_scraping_job(self, job):
        """Cancel a running scraping job."""
        try:
            if job.task_id:
                # Revoke the Celery task
                current_app.control.revoke(job.task_id, terminate=True)
            
            job.status = 'cancelled'
            job.completed_at = timezone.now()
            job.save()
            
            return True
        except Exception as e:
            job.error_message = f"Error cancelling job: {str(e)}"
            job.save()
            return False
    
    def _schedule_scraping_job(self, job):
        """Schedule a scraping job for later execution."""
        try:
            # Calculate delay in seconds
            delay = (job.scheduled_at - timezone.now()).total_seconds()
            
            if delay > 0:
                # Schedule the task
                task = scrape_marketplace.apply_async(
                    args=[job.id],
                    countdown=delay
                )
                
                job.task_id = task.id
                job.save()
                
                return True
        except Exception as e:
            job.status = 'failed'
            job.error_message = f"Error scheduling job: {str(e)}"
            job.save()
        
        return False
    
    def get_urls(self):
        """Add custom URLs for job actions."""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:job_id>/start/', self.admin_site.admin_view(self.start_job_view), name='scraping_scrapingjob_start'),
            path('<int:job_id>/cancel/', self.admin_site.admin_view(self.cancel_job_view), name='scraping_scrapingjob_cancel'),
        ]
        return custom_urls + urls
    
    def start_job_view(self, request, job_id):
        """View to start a specific job."""
        logger.info(f"Admin: start_job_view called for job_id: {job_id}")
        logger.info(f"Admin: Request user: {request.user}, Method: {request.method}")
        
        try:
            job = ScrapingJob.objects.get(id=job_id)
            logger.info(f"Admin: Found job {job_id}: {job.name} (status: {job.status})")
            
            if self._start_scraping_job(job):
                self.message_user(request, 'Scraping job started successfully.')
                logger.info(f"Admin: Job {job_id} started successfully via admin view")
            else:
                self.message_user(request, 'Failed to start scraping job.', level=messages.ERROR)
                logger.error(f"Admin: Failed to start job {job_id} via admin view")
        except ScrapingJob.DoesNotExist:
            logger.error(f"Admin: Job {job_id} not found")
            self.message_user(request, 'Job not found.', level=messages.ERROR)
        except Exception as e:
            logger.error(f"Admin: Unexpected error in start_job_view: {str(e)}")
            self.message_user(request, f'Error: {str(e)}', level=messages.ERROR)
        
        changelist_url = reverse('admin:scraping_scrapingjob_changelist')
        logger.info(f"Admin: Redirecting to: {changelist_url}")
        return HttpResponseRedirect(changelist_url)
    
    def cancel_job_view(self, request, job_id):
        """View to cancel a specific job."""
        try:
            job = ScrapingJob.objects.get(id=job_id)
            if self._cancel_scraping_job(job):
                self.message_user(request, 'Scraping job cancelled successfully.')
            else:
                self.message_user(request, 'Failed to cancel scraping job.', level=messages.ERROR)
        except ScrapingJob.DoesNotExist:
            self.message_user(request, 'Job not found.', level=messages.ERROR)
        
        return redirect(reverse('admin:scraping_scrapingjob_changelist'))
