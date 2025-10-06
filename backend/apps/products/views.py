"""
Views for products app.
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction, models

from .models import RegulatedProduct, RateListUpload
from .serializers import (
    RegulatedProductSerializer, RegulatedProductCreateSerializer,
    RateListUploadSerializer, RateListUploadCreateSerializer,
    PDFProcessingResultSerializer
)
from .pdf_processor import process_rate_list_pdf


class RegulatedProductListCreateView(generics.ListCreateAPIView):
    """List and create regulated products."""
    
    queryset = RegulatedProduct.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RegulatedProductCreateSerializer
        return RegulatedProductSerializer
    
    def perform_create(self, serializer):
        serializer.save()


class RegulatedProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a regulated product."""
    
    queryset = RegulatedProduct.objects.all()
    serializer_class = RegulatedProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class RateListUploadListCreateView(generics.ListCreateAPIView):
    """List and create rate list uploads."""
    
    queryset = RateListUpload.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RateListUploadCreateSerializer
        return RateListUploadSerializer
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class RateListUploadDetailView(generics.RetrieveAPIView):
    """Retrieve a rate list upload."""
    
    queryset = RateListUpload.objects.all()
    serializer_class = RateListUploadSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_rate_list_view(request):
    """Upload and process a rate list PDF."""
    
    if not request.user.is_admin:
        return Response(
            {'error': 'Only admins can upload rate lists'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if 'pdf_file' not in request.FILES:
        return Response(
            {'error': 'PDF file is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    pdf_file = request.FILES['pdf_file']
    name = request.data.get('name', f'Rate List - {timezone.now().strftime("%Y-%m-%d")}')
    
    # Create upload record
    upload = RateListUpload.objects.create(
        name=name,
        pdf_file=pdf_file,
        uploaded_by=request.user,
        status='processing'
    )
    
    try:
        # Process PDF
        result = process_rate_list_pdf(pdf_file)
        
        if result['success']:
            # Import products
            imported_count = 0
            errors = []
            
            with transaction.atomic():
                for product_data in result['products']:
                    try:
                        # Check if product already exists
                        existing_product = RegulatedProduct.objects.filter(
                            name__iexact=product_data['name']
                        ).first()
                        
                        if existing_product:
                            # Update existing product
                            existing_product.gov_price = product_data['gov_price']
                            existing_product.category = product_data['category']
                            existing_product.description = product_data['description']
                            existing_product.unit = product_data['unit']
                            existing_product.save()
                        else:
                            # Create new product
                            RegulatedProduct.objects.create(
                                name=product_data['name'],
                                gov_price=product_data['gov_price'],
                                category=product_data['category'],
                                description=product_data['description'],
                                unit=product_data['unit'],
                                is_active=True
                            )
                        
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Failed to import {product_data['name']}: {str(e)}")
            
            # Update upload record
            upload.status = 'completed'
            upload.total_products = result['total_products']
            upload.imported_products = imported_count
            upload.errors = errors + result['errors']
            upload.processed_at = timezone.now()
            upload.save()
            
            return Response({
                'message': 'Rate list processed successfully',
                'upload_id': upload.id,
                'total_products_found': result['total_products'],
                'imported_products': imported_count,
                'errors': errors + result['errors'],
                'success_rate': (imported_count / result['total_products'] * 100) if result['total_products'] > 0 else 0
            })
        
        else:
            # Processing failed
            upload.status = 'failed'
            upload.errors = result['errors']
            upload.processed_at = timezone.now()
            upload.save()
            
            return Response(
                {'error': 'Failed to process PDF', 'details': result['errors']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        upload.status = 'failed'
        upload.errors = [str(e)]
        upload.processed_at = timezone.now()
        upload.save()
        
        return Response(
            {'error': f'Processing failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def preview_pdf_processing_view(request):
    """Preview PDF processing without importing products."""
    
    if not request.user.is_admin:
        return Response(
            {'error': 'Only admins can preview PDF processing'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if 'pdf_file' not in request.FILES:
        return Response(
            {'error': 'PDF file is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    pdf_file = request.FILES['pdf_file']
    
    try:
        # Process PDF without importing
        result = process_rate_list_pdf(pdf_file)
        
        serializer = PDFProcessingResultSerializer(result)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': f'Preview failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def products_stats_view(request):
    """Get products statistics."""
    
    total_products = RegulatedProduct.objects.count()
    active_products = RegulatedProduct.objects.filter(is_active=True).count()
    
    # Products by category
    category_stats = RegulatedProduct.objects.values('category').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Recent uploads
    recent_uploads = RateListUpload.objects.filter(
        uploaded_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    
    return Response({
        'total_products': total_products,
        'active_products': active_products,
        'category_stats': list(category_stats),
        'recent_uploads': recent_uploads
    })