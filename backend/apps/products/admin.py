"""
Admin configuration for products app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect

from .models import RegulatedProduct, RateListUpload
from .pdf_processor import process_rate_list_pdf


@admin.register(RegulatedProduct)
class RegulatedProductAdmin(admin.ModelAdmin):
    """Admin for RegulatedProduct model."""
    
    list_display = [
        'name', 'category', 'gov_price', 'unit', 'is_active', 
        'created_at', 'updated_at'
    ]
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category']
    list_editable = ['gov_price', 'is_active']
    ordering = ['name']
    list_per_page = 50
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('gov_price', 'unit')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(RateListUpload)
class RateListUploadAdmin(admin.ModelAdmin):
    """Admin for RateListUpload model."""
    
    list_display = [
        'name', 'uploaded_by', 'status', 'total_products', 
        'imported_products', 'success_rate_display', 'uploaded_at'
    ]
    list_filter = ['status', 'uploaded_at', 'uploaded_by']
    search_fields = ['name', 'uploaded_by__username']
    readonly_fields = [
        'uploaded_by', 'uploaded_at', 'processed_at', 'total_products',
        'imported_products', 'errors', 'success_rate_display'
    ]
    ordering = ['-uploaded_at']
    list_per_page = 25
    actions = ['process_selected_uploads', 'preview_selected_uploads']
    
    fieldsets = (
        ('Upload Information', {
            'fields': ('name', 'pdf_file', 'uploaded_by', 'uploaded_at')
        }),
        ('Processing Results', {
            'fields': ('status', 'total_products', 'imported_products', 'success_rate_display', 'processed_at')
        }),
        ('Errors', {
            'fields': ('errors',),
            'classes': ('collapse',)
        }),
    )
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Add custom context for the change view."""
        extra_context = extra_context or {}
        try:
            upload = RateListUpload.objects.get(id=object_id)
            extra_context['can_process'] = upload.status == 'pending'
            extra_context['can_preview'] = True
            extra_context['upload'] = upload
        except RateListUpload.DoesNotExist:
            extra_context['can_process'] = False
            extra_context['can_preview'] = False
            extra_context['upload'] = None
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    def changelist_view(self, request, extra_context=None):
        """Add custom context for the changelist view."""
        extra_context = extra_context or {}
        pending_uploads = RateListUpload.objects.filter(status='pending').count()
        extra_context['pending_uploads_count'] = pending_uploads
        return super().changelist_view(request, extra_context)
    
    def success_rate_display(self, obj):
        """Display success rate with color coding."""
        rate = obj.success_rate
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
        
        # Format the rate as a string first
        rate_str = f"{rate:.1f}%"
        
        return format_html(
            '<span style="color: {};">{}</span>',
            color, 
            rate_str
        )
    success_rate_display.short_description = 'Success Rate'
    
    def get_urls(self):
        """Add custom URLs for processing."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:upload_id>/process/',
                self.admin_site.admin_view(self.process_upload_view),
                name='products_ratelistupload_process'
            ),
            path(
                '<int:upload_id>/preview/',
                self.admin_site.admin_view(self.preview_upload_view),
                name='products_ratelistupload_preview'
            ),
        ]
        return custom_urls + urls
    
    def process_upload_view(self, request, upload_id):
        """Process uploaded PDF."""
        upload = RateListUpload.objects.get(id=upload_id)
        
        if upload.status != 'pending':
            messages.error(request, f"Upload is already {upload.status}")
            return HttpResponseRedirect(
                reverse('admin:products_ratelistupload_change', args=[upload_id])
            )
        
        try:
            # Process PDF
            result = process_rate_list_pdf(upload.pdf_file)
            
            if result['success']:
                # Import products
                imported_count = 0
                errors = []
                
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
                upload.save()
                
                messages.success(
                    request, 
                    f"Successfully imported {imported_count} products from {result['total_products']} found"
                )
            else:
                upload.status = 'failed'
                upload.errors = result['errors']
                upload.save()
                
                messages.error(request, f"Processing failed: {', '.join(result['errors'])}")
        
        except Exception as e:
            upload.status = 'failed'
            upload.errors = [str(e)]
            upload.save()
            
            messages.error(request, f"Processing failed: {str(e)}")
        
        return HttpResponseRedirect(
            reverse('admin:products_ratelistupload_change', args=[upload_id])
        )
    
    def preview_upload_view(self, request, upload_id):
        """Preview PDF processing results."""
        upload = RateListUpload.objects.get(id=upload_id)
        
        try:
            result = process_rate_list_pdf(upload.pdf_file)
            
            if result['success']:
                messages.info(
                    request, 
                    f"Preview: Found {result['total_products']} products. "
                    f"First few: {', '.join([p['name'] for p in result['products'][:3]])}"
                )
            else:
                messages.error(request, f"Preview failed: {', '.join(result['errors'])}")
        
        except Exception as e:
            messages.error(request, f"Preview failed: {str(e)}")
        
        return HttpResponseRedirect(
            reverse('admin:products_ratelistupload_change', args=[upload_id])
        )
    
    def save_model(self, request, obj, form, change):
        """Set uploaded_by when creating new upload."""
        if not change:  # Creating new object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def process_selected_uploads(self, request, queryset):
        """Process selected uploads."""
        processed_count = 0
        for upload in queryset:
            if upload.status == 'pending':
                try:
                    # Process PDF
                    result = process_rate_list_pdf(upload.pdf_file)
                    
                    if result['success']:
                        # Import products
                        imported_count = 0
                        errors = []
                        
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
                        upload.save()
                        
                        processed_count += 1
                        self.message_user(request, f"Successfully processed '{upload.name}' - imported {imported_count} products")
                    else:
                        upload.status = 'failed'
                        upload.errors = result['errors']
                        upload.save()
                        self.message_user(request, f"Failed to process '{upload.name}': {', '.join(result['errors'])}", level=messages.ERROR)
                
                except Exception as e:
                    upload.status = 'failed'
                    upload.errors = [str(e)]
                    upload.save()
                    self.message_user(request, f"Error processing '{upload.name}': {str(e)}", level=messages.ERROR)
            else:
                self.message_user(request, f"'{upload.name}' is already {upload.status}", level=messages.WARNING)
        
        if processed_count > 0:
            self.message_user(request, f"Successfully processed {processed_count} upload(s)")
    
    process_selected_uploads.short_description = "Process selected uploads"
    
    def preview_selected_uploads(self, request, queryset):
        """Preview selected uploads."""
        for upload in queryset:
            try:
                result = process_rate_list_pdf(upload.pdf_file)
                
                if result['success']:
                    self.message_user(
                        request, 
                        f"Preview for '{upload.name}': Found {result['total_products']} products. "
                        f"First few: {', '.join([p['name'] for p in result['products'][:3]])}"
                    )
                else:
                    self.message_user(request, f"Preview failed for '{upload.name}': {', '.join(result['errors'])}", level=messages.ERROR)
            
            except Exception as e:
                self.message_user(request, f"Preview failed for '{upload.name}': {str(e)}", level=messages.ERROR)
    
    preview_selected_uploads.short_description = "Preview selected uploads"