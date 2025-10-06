from django.urls import path
from .views import (
    ScrapedProductListView, ScrapingJobListCreateView, ScrapingJobDetailView,
    ScrapingWebsiteListCreateView, ScrapingWebsiteDetailView,
    ProductSearchListListCreateView, ProductSearchListDetailView,
    scraping_stats_view, trigger_scraping_view, cancel_scraping_job_view,
    cleanup_old_data_view, test_website_scraping_view
)

urlpatterns = [
    # Scraped Products
    path('results/', ScrapedProductListView.as_view(), name='scraped_products'),
    
    # Scraping Jobs
    path('jobs/', ScrapingJobListCreateView.as_view(), name='scraping_jobs'),
    path('jobs/<int:pk>/', ScrapingJobDetailView.as_view(), name='scraping_job_detail'),
    path('jobs/<int:job_id>/cancel/', cancel_scraping_job_view, name='cancel_scraping_job'),
    
    # Scraping Websites
    path('websites/', ScrapingWebsiteListCreateView.as_view(), name='scraping_websites'),
    path('websites/<int:pk>/', ScrapingWebsiteDetailView.as_view(), name='scraping_website_detail'),
    path('websites/<int:website_id>/test/', test_website_scraping_view, name='test_website_scraping'),
    
    # Product Search Lists
    path('product-lists/', ProductSearchListListCreateView.as_view(), name='product_search_lists'),
    path('product-lists/<int:pk>/', ProductSearchListDetailView.as_view(), name='product_search_list_detail'),
    
    # Utility endpoints
    path('stats/', scraping_stats_view, name='scraping_stats'),
    path('trigger/', trigger_scraping_view, name='trigger_scraping'),
    path('cleanup/', cleanup_old_data_view, name='cleanup_old_data'),
]
