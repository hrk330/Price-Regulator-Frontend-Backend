"""
URLs for products app.
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Regulated Products
    path('regulated-products/', views.RegulatedProductListCreateView.as_view(), name='regulated-product-list'),
    path('regulated-products/<int:pk>/', views.RegulatedProductDetailView.as_view(), name='regulated-product-detail'),
    
    # Rate List Uploads
    path('rate-list-uploads/', views.RateListUploadListCreateView.as_view(), name='rate-list-upload-list'),
    path('rate-list-uploads/<int:pk>/', views.RateListUploadDetailView.as_view(), name='rate-list-upload-detail'),
    
    # PDF Processing
    path('upload-rate-list/', views.upload_rate_list_view, name='upload-rate-list'),
    path('preview-pdf-processing/', views.preview_pdf_processing_view, name='preview-pdf-processing'),
    
    # Statistics
    path('stats/', views.products_stats_view, name='products-stats'),
]