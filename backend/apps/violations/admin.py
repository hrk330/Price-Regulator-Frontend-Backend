from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Violation, ViolationCheckReport


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = [
        'regulated_product', 'scraped_product_name', 'violation_type', 'severity', 'status',
        'proposed_penalty', 'price_difference_display', 'percentage_over_display', 'confirmed_by', 'created_at'
    ]
    list_filter = ['status', 'severity', 'violation_type', 'created_at', 'scraped_product__marketplace']
    search_fields = ['regulated_product__name', 'scraped_product__product_name', 'notes']
    readonly_fields = ['created_at', 'confirmed_at', 'price_difference_display', 'percentage_over_display']
    ordering = ['-created_at']
    list_per_page = 50  # Pagination for better performance
    list_max_show_all = 200  # Limit bulk operations
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset(request).select_related(
            'regulated_product', 'scraped_product', 'confirmed_by'
        ).prefetch_related('case')
    
    def save_model(self, request, obj, form, change):
        """Override save to set confirmed_by when status changes to confirmed."""
        if change and obj.status == 'confirmed' and not obj.confirmed_by:
            obj.confirmed_by = request.user
            if not obj.confirmed_at:
                from django.utils import timezone
                obj.confirmed_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    actions = ['confirm_violations', 'dismiss_violations']
    
    def confirm_violations(self, request, queryset):
        """Confirm selected violations and create cases."""
        from django.utils import timezone
        from apps.cases.models import Case
        
        confirmed_count = 0
        cases_created = 0
        
        for violation in queryset.filter(status='pending'):
            violation.status = 'confirmed'
            violation.confirmed_by = request.user
            violation.confirmed_at = timezone.now()
            violation.save()
            confirmed_count += 1
            
            # Create case if it doesn't exist
            if not Case.objects.filter(violation=violation).exists():
                Case.objects.create(
                    violation=violation,
                    investigator=request.user,
                    status='open',
                    notes=f"Case created from confirmed violation: {violation.violation_type}"
                )
                cases_created += 1
        
        self.message_user(
            request,
            f"Confirmed {confirmed_count} violations and created {cases_created} new cases."
        )
    confirm_violations.short_description = "Confirm selected violations and create cases"
    
    def dismiss_violations(self, request, queryset):
        """Dismiss selected violations."""
        from django.utils import timezone
        
        dismissed_count = 0
        for violation in queryset.filter(status='pending'):
            violation.status = 'dismissed'
            violation.confirmed_by = request.user
            violation.confirmed_at = timezone.now()
            violation.save()
            dismissed_count += 1
        
        self.message_user(
            request,
            f"Dismissed {dismissed_count} violations."
        )
    dismiss_violations.short_description = "Dismiss selected violations"
    
    fieldsets = (
        ('Violation Details', {
            'fields': ('regulated_product', 'scraped_product', 'violation_type', 'severity')
        }),
        ('Price Information', {
            'fields': ('price_difference_display', 'percentage_over_display', 'proposed_penalty', 'status')
        }),
        ('Investigation', {
            'fields': ('notes', 'confirmed_by', 'confirmed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def scraped_product_name(self, obj):
        """Display scraped product name with marketplace."""
        if obj.scraped_product:
            return f"{obj.scraped_product.product_name} ({obj.scraped_product.marketplace})"
        return "N/A"
    scraped_product_name.short_description = "Scraped Product"
    
    def price_difference_display(self, obj):
        """Display price difference with color coding."""
        if obj.scraped_product and obj.regulated_product:
            diff = obj.price_difference
            color = "red" if diff > 0 else "green"
            return format_html(
                '<span style="color: {};">Rs.{}</span>',
                color, diff
            )
        return "N/A"
    price_difference_display.short_description = "Price Difference"
    
    def percentage_over_display(self, obj):
        """Display percentage over with color coding."""
        if obj.scraped_product and obj.regulated_product:
            pct = obj.percentage_over
            color = "red" if pct > 0 else "green"
            pct_formatted = f"{pct:.1f}"
            return format_html(
                '<span style="color: {};">{}%</span>',
                color, pct_formatted
            )
        return "N/A"
    percentage_over_display.short_description = "% Over Regulated Price"


@admin.register(ViolationCheckReport)
class ViolationCheckReportAdmin(admin.ModelAdmin):
    list_display = [
        'scraped_product_name', 'regulated_product_name', 'compliance_status_display',
        'scraped_price_display', 'regulated_price_display', 'price_difference_display',
        'percentage_difference_display', 'marketplace', 'check_date'
    ]
    list_filter = [
        'compliance_status', 'has_violation', 'violation_severity', 
        'check_date', 'scraped_product__marketplace'
    ]
    search_fields = [
        'scraped_product__product_name', 'regulated_product__name',
        'scraped_product__seller_name', 'notes'
    ]
    readonly_fields = [
        'check_date', 'scraped_price_display', 'regulated_price_display',
        'price_difference_display', 'percentage_difference_display'
    ]
    ordering = ['-check_date']
    list_per_page = 100  # Pagination for better performance
    list_max_show_all = 500  # Limit bulk operations
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset(request).select_related(
            'regulated_product', 'scraped_product', 'violation_record'
        )
    
    fieldsets = (
        ('Product Information', {
            'fields': ('scraped_product', 'regulated_product', 'compliance_status')
        }),
        ('Price Comparison', {
            'fields': (
                'scraped_price_display', 'regulated_price_display', 
                'price_difference_display', 'percentage_difference_display'
            )
        }),
        ('Violation Details', {
            'fields': ('has_violation', 'violation_severity', 'proposed_penalty', 'violation_record')
        }),
        ('Additional Information', {
            'fields': ('notes', 'check_date')
        }),
    )
    
    def scraped_product_name(self, obj):
        """Display scraped product name with marketplace."""
        return f"{obj.scraped_product.product_name} ({obj.scraped_product.marketplace})"
    scraped_product_name.short_description = "Scraped Product"
    
    def regulated_product_name(self, obj):
        """Display regulated product name."""
        if obj.regulated_product:
            return obj.regulated_product.name
        return "No Match"
    regulated_product_name.short_description = "Regulated Product"
    
    def compliance_status_display(self, obj):
        """Display compliance status with color coding."""
        colors = {
            'ok': 'green',
            'violation': 'red',
            'no_match': 'orange'
        }
        color = colors.get(obj.compliance_status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_compliance_status_display()
        )
    compliance_status_display.short_description = "Status"
    
    def scraped_price_display(self, obj):
        """Display scraped price."""
        return f"Rs.{obj.scraped_price}"
    scraped_price_display.short_description = "Scraped Price"
    
    def regulated_price_display(self, obj):
        """Display regulated price."""
        if obj.regulated_price:
            return f"Rs.{obj.regulated_price}"
        return "N/A"
    regulated_price_display.short_description = "Regulated Price"
    
    def price_difference_display(self, obj):
        """Display price difference with color coding."""
        if obj.price_difference is not None:
            color = "red" if obj.price_difference > 0 else "green"
            return format_html(
                '<span style="color: {};">Rs.{}</span>',
                color, obj.price_difference
            )
        return "N/A"
    price_difference_display.short_description = "Price Difference"
    
    def percentage_difference_display(self, obj):
        """Display percentage difference with color coding."""
        if obj.percentage_difference is not None:
            color = "red" if obj.percentage_difference > 0 else "green"
            pct_formatted = f"{obj.percentage_difference:.1f}"
            return format_html(
                '<span style="color: {};">{}%</span>',
                color, pct_formatted
            )
        return "N/A"
    percentage_difference_display.short_description = "% Difference"
    
    def marketplace(self, obj):
        """Display marketplace."""
        return obj.marketplace
    marketplace.short_description = "Marketplace"
    
    actions = ['run_violation_check', 'export_violation_report']
    
    def run_violation_check(self, request, queryset):
        """Run violation check on selected reports."""
        from django.core.management import call_command
        from io import StringIO
        
        # Get unique scraped products from selected reports
        scraped_product_ids = queryset.values_list('scraped_product_id', flat=True).distinct()
        
        # Run the violation check command
        output = StringIO()
        call_command('check_all_violations', stdout=output)
        
        self.message_user(
            request,
            f"Violation check completed for {len(scraped_product_ids)} products. "
            f"Check the output for details."
        )
    run_violation_check.short_description = "Run violation check on selected products"
    
    def export_violation_report(self, request, queryset):
        """Export violation report for selected items."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="violation_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Scraped Product', 'Marketplace', 'Regulated Product', 'Compliance Status',
            'Scraped Price', 'Regulated Price', 'Price Difference', 'Percentage Difference',
            'Violation Severity', 'Proposed Penalty', 'Check Date', 'Notes'
        ])
        
        for report in queryset:
            writer.writerow([
                report.scraped_product.product_name,
                report.marketplace,
                report.regulated_product.name if report.regulated_product else 'No Match',
                report.get_compliance_status_display(),
                report.scraped_price,
                report.regulated_price or 'N/A',
                report.price_difference or 'N/A',
                f"{report.percentage_difference}%" if report.percentage_difference else 'N/A',
                report.get_violation_severity_display() if report.violation_severity else 'N/A',
                report.proposed_penalty or 'N/A',
                report.check_date.strftime('%Y-%m-%d %H:%M:%S'),
                report.notes
            ])
        
        return response
    export_violation_report.short_description = "Export violation report to CSV"
