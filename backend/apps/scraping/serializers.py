from rest_framework import serializers
from .models import ScrapedProduct, ScrapingJob, ScrapingWebsite, ProductSearchList


class ScrapingWebsiteSerializer(serializers.ModelSerializer):
    """Serializer for ScrapingWebsite model."""
    
    class Meta:
        model = ScrapingWebsite
        fields = [
            'id', 'name', 'base_url', 'search_url_template', 'is_active',
            'scraping_config', 'rate_limit_delay', 'headers', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSearchListSerializer(serializers.ModelSerializer):
    """Serializer for ProductSearchList model."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductSearchList
        fields = [
            'id', 'name', 'description', 'products', 'is_active',
            'created_by', 'created_by_name', 'products_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        return len(obj.products) if obj.products else 0


class ScrapedProductSerializer(serializers.ModelSerializer):
    """Serializer for ScrapedProduct model."""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = ScrapedProduct
        fields = [
            'id', 'product_name', 'marketplace', 'website', 'website_name',
            'search_query', 'listed_price', 'original_price', 'url', 'image_url',
            'description', 'availability', 'stock_status', 'seller_name',
            'rating', 'review_count', 'scraped_at', 'scraping_job'
        ]
        read_only_fields = ['id', 'scraped_at']


class ScrapingJobSerializer(serializers.ModelSerializer):
    """Serializer for ScrapingJob model."""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    product_list_name = serializers.CharField(source='product_list.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ScrapingJob
        fields = [
            'id', 'name', 'website', 'website_name', 'product_list', 'product_list_name',
            'marketplace', 'status', 'products_scraped', 'products_found', 'errors_count',
            'started_at', 'completed_at', 'error_message', 'created_by', 'created_by_name',
            'created_at', 'task_id'
        ]
        read_only_fields = [
            'id', 'status', 'products_scraped', 'products_found', 'errors_count',
            'started_at', 'completed_at', 'error_message', 'created_at', 'task_id'
        ]


class ScrapingJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ScrapingJob."""
    
    class Meta:
        model = ScrapingJob
        fields = ['name', 'website', 'product_list', 'marketplace']
    
    def validate(self, data):
        """Validate that website is active and product list is provided."""
        website = data.get('website')
        if website and not website.is_active:
            raise serializers.ValidationError("Selected website is not active")
        
        product_list = data.get('product_list')
        if product_list and not product_list.is_active:
            raise serializers.ValidationError("Selected product list is not active")
        
        return data


class ScrapingJobUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ScrapingJob status."""
    
    class Meta:
        model = ScrapingJob
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance and self.instance.status in ['completed', 'failed']:
            if value not in ['completed', 'failed']:
                raise serializers.ValidationError("Cannot change status of completed/failed job")
        return value
