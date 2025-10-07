from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class Violation(models.Model):
    """Price violations detected by the system."""
    
    VIOLATION_TYPE_CHOICES = [
        ('price_exceeded', 'Price Exceeded'),
        ('price_not_listed', 'Price Not Listed'),
        ('misleading_pricing', 'Misleading Pricing'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('dismissed', 'Dismissed'),
    ]
    
    regulated_product = models.ForeignKey(
        'products.RegulatedProduct',
        on_delete=models.CASCADE,
        related_name='violations'
    )
    scraped_product = models.ForeignKey(
        'scraping.ScrapedProduct',
        on_delete=models.CASCADE,
        related_name='violations',
        null=True,
        blank=True
    )
    violation_type = models.CharField(max_length=50, choices=VIOLATION_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    proposed_penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    confirmed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_violations'
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['regulated_product', 'status']),
        ]
    
    def __str__(self):
        return f"{self.regulated_product.name} - {self.violation_type} - {self.severity}"
    
    @property
    def price_difference(self):
        """Calculate the difference between scraped and regulated price."""
        return self.scraped_product.listed_price - self.regulated_product.gov_price
    
    @property
    def percentage_over(self):
        """Calculate percentage over the regulated price."""
        if self.regulated_product.gov_price > 0:
            return (self.price_difference / self.regulated_product.gov_price) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Override save to automatically create cases when status changes to confirmed."""
        from django.core.cache import cache
        
        # Check if this is an update and status is changing to 'confirmed'
        if self.pk:  # This is an update, not a new creation
            try:
                old_violation = Violation.objects.get(pk=self.pk)
                old_status = old_violation.status
                
                # If status is changing from something else to 'confirmed'
                if old_status != 'confirmed' and self.status == 'confirmed':
                    # Set confirmed_by and confirmed_at if not already set
                    if not self.confirmed_by:
                        # Try to get the current user from the request context
                        # This is a fallback - ideally this should be set by the admin/API
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        admin_user = User.objects.filter(role='admin').first()
                        if admin_user:
                            self.confirmed_by = admin_user
                    
                    if not self.confirmed_at:
                        self.confirmed_at = timezone.now()
                    
                    # Create case if it doesn't exist
                    from apps.cases.models import Case
                    if not Case.objects.filter(violation=self).exists():
                        investigator = self.confirmed_by if self.confirmed_by else admin_user
                        Case.objects.create(
                            violation=self,
                            investigator=investigator,
                            status='open',
                            notes=f"Case created from confirmed violation: {self.violation_type}"
                        )
            except Violation.DoesNotExist:
                pass  # This is a new violation, no old status to compare
        
        super().save(*args, **kwargs)
        
        # Invalidate cache when violations are updated
        cache.delete('full_violation_report')
        cache.delete('violation_stats')


class ViolationCheckReport(models.Model):
    """Comprehensive report tracking all product comparisons (violations + compliant)."""
    
    COMPLIANCE_STATUS_CHOICES = [
        ('ok', 'Compliant'),
        ('violation', 'Violation'),
        ('no_match', 'No Matching Regulated Product'),
    ]
    
    regulated_product = models.ForeignKey(
        'products.RegulatedProduct',
        on_delete=models.CASCADE,
        related_name='check_reports',
        null=True,
        blank=True,
        help_text="Regulated product (null if no match found)"
    )
    scraped_product = models.ForeignKey(
        'scraping.ScrapedProduct',
        on_delete=models.CASCADE,
        related_name='check_reports'
    )
    check_date = models.DateTimeField(auto_now_add=True)
    has_violation = models.BooleanField(default=False)
    compliance_status = models.CharField(
        max_length=20, 
        choices=COMPLIANCE_STATUS_CHOICES,
        default='no_match'
    )
    price_difference = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Difference between scraped and regulated price"
    )
    percentage_difference = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage difference from regulated price"
    )
    violation_severity = models.CharField(
        max_length=20,
        choices=Violation.SEVERITY_CHOICES,
        null=True,
        blank=True
    )
    proposed_penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    violation_record = models.ForeignKey(
        'Violation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Associated violation record if any"
    )
    
    class Meta:
        ordering = ['-check_date']
        indexes = [
            models.Index(fields=['compliance_status', 'check_date']),
            models.Index(fields=['scraped_product', 'check_date']),
            models.Index(fields=['has_violation', 'check_date']),
        ]
        unique_together = ['regulated_product', 'scraped_product']
    
    def __str__(self):
        if self.regulated_product:
            return f"{self.scraped_product.product_name} vs {self.regulated_product.name} - {self.compliance_status}"
        return f"{self.scraped_product.product_name} - {self.compliance_status}"
    
    @property
    def regulated_price(self):
        """Get regulated price if available."""
        return self.regulated_product.gov_price if self.regulated_product else None
    
    @property
    def scraped_price(self):
        """Get scraped price."""
        return self.scraped_product.listed_price
    
    @property
    def marketplace(self):
        """Get marketplace from scraped product."""
        return self.scraped_product.marketplace
    
    @property
    def seller_name(self):
        """Get seller name from scraped product."""
        return self.scraped_product.seller_name
