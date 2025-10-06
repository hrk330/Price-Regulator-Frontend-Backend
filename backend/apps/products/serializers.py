"""
Serializers for products app.
"""
from rest_framework import serializers
from .models import RegulatedProduct, RateListUpload


class RegulatedProductSerializer(serializers.ModelSerializer):
    """Serializer for RegulatedProduct model."""
    
    class Meta:
        model = RegulatedProduct
        fields = [
            'id', 'name', 'category', 'gov_price', 'description', 
            'unit', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegulatedProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating RegulatedProduct."""
    
    class Meta:
        model = RegulatedProduct
        fields = [
            'name', 'category', 'gov_price', 'description', 
            'unit', 'is_active'
        ]


class RateListUploadSerializer(serializers.ModelSerializer):
    """Serializer for RateListUpload model."""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = RateListUpload
        fields = [
            'id', 'name', 'pdf_file', 'status', 'total_products', 
            'imported_products', 'errors', 'uploaded_by_name', 
            'uploaded_at', 'processed_at', 'success_rate'
        ]
        read_only_fields = [
            'id', 'status', 'total_products', 'imported_products', 
            'errors', 'uploaded_at', 'processed_at', 'success_rate'
        ]


class RateListUploadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating RateListUpload."""
    
    class Meta:
        model = RateListUpload
        fields = ['name', 'pdf_file']
    
    def validate_pdf_file(self, value):
        """Validate uploaded PDF file."""
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        return value


class PDFProcessingResultSerializer(serializers.Serializer):
    """Serializer for PDF processing results."""
    
    success = serializers.BooleanField()
    products = serializers.ListField(child=serializers.DictField())
    total_products = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.CharField())