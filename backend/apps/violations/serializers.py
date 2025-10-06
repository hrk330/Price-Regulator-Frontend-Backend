from rest_framework import serializers
from .models import Violation
from apps.products.serializers import RegulatedProductSerializer
from apps.scraping.serializers import ScrapedProductSerializer
from apps.accounts.serializers import UserSerializer


class ViolationSerializer(serializers.ModelSerializer):
    """Serializer for Violation model."""
    
    regulated_product = RegulatedProductSerializer(read_only=True)
    scraped_product = ScrapedProductSerializer(read_only=True)
    confirmed_by = UserSerializer(read_only=True)
    price_difference = serializers.ReadOnlyField()
    percentage_over = serializers.ReadOnlyField()
    
    class Meta:
        model = Violation
        fields = [
            'id', 'regulated_product', 'scraped_product', 'violation_type',
            'severity', 'proposed_penalty', 'status', 'notes', 'confirmed_by',
            'confirmed_at', 'price_difference', 'percentage_over', 'created_at'
        ]
        read_only_fields = [
            'id', 'regulated_product', 'scraped_product', 'violation_type',
            'severity', 'proposed_penalty', 'confirmed_by', 'confirmed_at',
            'created_at'
        ]


class ViolationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating violation status and notes."""
    
    class Meta:
        model = Violation
        fields = ['status', 'notes']
    
    def validate_status(self, value):
        if value not in ['confirmed', 'dismissed']:
            raise serializers.ValidationError("Status must be 'confirmed' or 'dismissed'.")
        return value
