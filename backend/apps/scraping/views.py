from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from .models import ScrapedProduct, ScrapingJob, ScrapingWebsite, ProductSearchList
from .serializers import (
    ScrapedProductSerializer, ScrapingJobSerializer, ScrapingJobCreateSerializer,
    ScrapingJobUpdateSerializer, ScrapingWebsiteSerializer, ProductSearchListSerializer
)
from .tasks import scrape_marketplace, cleanup_old_scraped_products


class ScrapedProductListView(generics.ListAPIView):
    """List scraped products."""
    
    serializer_class = ScrapedProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ScrapedProduct.objects.select_related('website', 'scraping_job')
        
        # Filter by marketplace
        marketplace = self.request.query_params.get('marketplace')
        if marketplace:
            queryset = queryset.filter(marketplace=marketplace)
        
        # Filter by website
        website = self.request.query_params.get('website')
        if website:
            queryset = queryset.filter(website_id=website)
        
        # Filter by availability
        availability = self.request.query_params.get('availability')
        if availability is not None:
            queryset = queryset.filter(availability=availability.lower() == 'true')
        
        # Search by product name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(product_name__icontains=search)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(scraped_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(scraped_at__date__lte=date_to)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(listed_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(listed_price__lte=max_price)
        
        return queryset


class ScrapingJobListCreateView(generics.ListCreateAPIView):
    """List and create scraping jobs."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ScrapingJobCreateSerializer
        return ScrapingJobSerializer
    
    def get_queryset(self):
        queryset = ScrapingJob.objects.select_related('website', 'product_list', 'created_by')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by website
        website = self.request.query_params.get('website')
        if website:
            queryset = queryset.filter(website_id=website)
        
        return queryset
    
    def perform_create(self, serializer):
        # Only admins can create scraping jobs
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admins can create scraping jobs.")
        
        job = serializer.save(created_by=self.request.user)
        
        # Start the scraping task
        task = scrape_marketplace.delay(job.id)
        job.task_id = task.id
        job.save()


class ScrapingJobDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update a scraping job."""
    
    queryset = ScrapingJob.objects.select_related('website', 'product_list', 'created_by')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ScrapingJobUpdateSerializer
        return ScrapingJobSerializer


class ScrapingWebsiteListCreateView(generics.ListCreateAPIView):
    """List and create scraping websites."""
    
    queryset = ScrapingWebsite.objects.all()
    serializer_class = ScrapingWebsiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Only admins can create websites
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admins can create scraping websites.")


class ScrapingWebsiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a scraping website."""
    
    queryset = ScrapingWebsite.objects.all()
    serializer_class = ScrapingWebsiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        # Only admins can update websites
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admins can update scraping websites.")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only admins can delete websites
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admins can delete scraping websites.")
        instance.delete()


class ProductSearchListListCreateView(generics.ListCreateAPIView):
    """List and create product search lists."""
    
    serializer_class = ProductSearchListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ProductSearchList.objects.select_related('created_by')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        # Only admins can create product lists
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admins can create product search lists.")
        serializer.save(created_by=self.request.user)


class ProductSearchListDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a product search list."""
    
    queryset = ProductSearchList.objects.select_related('created_by')
    serializer_class = ProductSearchListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        # Only admins can update product lists
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admins can update product search lists.")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only admins can delete product lists
        if not self.request.user.is_admin:
            raise permissions.PermissionDenied("Only admins can delete product search lists.")
        instance.delete()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@cache_page(60 * 5)  # Cache for 5 minutes
def scraping_stats_view(request):
    """Get scraping statistics."""
    
    # Check cache first
    cache_key = 'scraping_stats'
    cached_stats = cache.get(cache_key)
    if cached_stats:
        return Response(cached_stats)
    
    # Total products scraped
    total_products = ScrapedProduct.objects.count()
    
    # Products by marketplace
    marketplace_stats = ScrapedProduct.objects.values('marketplace').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Products by website
    website_stats = ScrapedProduct.objects.values('website__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent scraping activity
    recent_jobs = ScrapingJob.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    # Active jobs
    active_jobs = ScrapingJob.objects.filter(
        status__in=['pending', 'running']
    ).count()
    
    # Average price by marketplace
    avg_prices = ScrapedProduct.objects.values('marketplace').annotate(
        avg_price=Count('listed_price')
    ).order_by('-avg_price')
    
    stats_data = {
        'total_products_scraped': total_products,
        'marketplace_stats': list(marketplace_stats),
        'website_stats': list(website_stats),
        'recent_jobs_count': recent_jobs,
        'active_jobs_count': active_jobs,
        'avg_prices': list(avg_prices),
    }
    
    # Cache the stats for 5 minutes
    cache.set(cache_key, stats_data, 300)
    
    return Response(stats_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def trigger_scraping_view(request):
    """Manually trigger a scraping job."""
    
    if not request.user.is_admin:
        return Response(
            {'error': 'Only admins can trigger scraping jobs'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    website_id = request.data.get('website_id')
    product_list_id = request.data.get('product_list_id')
    marketplace = request.data.get('marketplace', 'other')
    
    if not website_id:
        return Response(
            {'error': 'Website ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        website = get_object_or_404(ScrapingWebsite, id=website_id, is_active=True)
        product_list = None
        
        if product_list_id:
            product_list = get_object_or_404(ProductSearchList, id=product_list_id, is_active=True)
        
        # Create and start scraping job
        job = ScrapingJob.objects.create(
            name=f"Manual scraping - {website.name}",
            website=website,
            product_list=product_list,
            marketplace=marketplace,
            created_by=request.user
        )
        
        # Start the scraping task
        task = scrape_marketplace.delay(job.id)
        job.task_id = task.id
        job.save()
        
        return Response({
            'message': 'Scraping job started',
            'job_id': job.id,
            'job_name': job.name,
            'task_id': task.id
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_scraping_job_view(request, job_id):
    """Cancel a running scraping job."""
    
    if not request.user.is_admin:
        return Response(
            {'error': 'Only admins can cancel scraping jobs'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        job = get_object_or_404(ScrapingJob, id=job_id)
        
        if job.status not in ['pending', 'running']:
            return Response(
                {'error': 'Job is not in a cancellable state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel the Celery task if it exists
        if job.task_id:
            from celery import current_app
            current_app.control.revoke(job.task_id, terminate=True)
        
        # Update job status
        job.status = 'cancelled'
        job.completed_at = timezone.now()
        job.save()
        
        return Response({
            'message': 'Scraping job cancelled',
            'job_id': job.id
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cleanup_old_data_view(request):
    """Clean up old scraped products."""
    
    if not request.user.is_admin:
        return Response(
            {'error': 'Only admins can clean up old data'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    days_old = request.data.get('days_old', 30)
    
    # Start cleanup task
    task = cleanup_old_scraped_products.delay(days_old)
    
    return Response({
        'message': f'Cleanup task started for products older than {days_old} days',
        'task_id': task.id
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def test_website_scraping_view(request, website_id):
    """Test scraping configuration for a website."""
    
    if not request.user.is_admin:
        return Response(
            {'error': 'Only admins can test scraping configurations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        website = get_object_or_404(ScrapingWebsite, id=website_id)
        test_query = request.query_params.get('query', 'test product')
        
        # Initialize scraping engine
        website_config = {
            'base_url': website.base_url,
            'search_url_template': website.search_url_template,
            'scraping_config': website.scraping_config,
            'rate_limit_delay': website.rate_limit_delay,
            'headers': website.headers,
            'marketplace': 'other'
        }
        
        from .scraping_engines import get_scraping_engine
        scraping_engine = get_scraping_engine(website_config)
        
        # Test scraping
        results = scraping_engine.search_products(test_query, max_results=3)
        
        return Response({
            'message': 'Test completed',
            'website': website.name,
            'test_query': test_query,
            'results_found': len(results),
            'sample_results': results[:3]  # Return first 3 results
        })
        
    except Exception as e:
        return Response(
            {'error': f'Test failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
