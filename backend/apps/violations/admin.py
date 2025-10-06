from django.contrib import admin
from .models import Violation


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = [
        'regulated_product', 'violation_type', 'severity', 'status',
        'proposed_penalty', 'confirmed_by', 'created_at'
    ]
    list_filter = ['status', 'severity', 'violation_type', 'created_at']
    search_fields = ['regulated_product__name', 'scraped_product__product_name', 'notes']
    readonly_fields = ['created_at', 'confirmed_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Violation Details', {
            'fields': ('regulated_product', 'scraped_product', 'violation_type', 'severity')
        }),
        ('Penalty Information', {
            'fields': ('proposed_penalty', 'status')
        }),
        ('Investigation', {
            'fields': ('notes', 'confirmed_by', 'confirmed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
