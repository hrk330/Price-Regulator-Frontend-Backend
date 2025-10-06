from django.db import models
from django.core.validators import MinValueValidator
from django.core.files.storage import default_storage


class RateListUpload(models.Model):
    """Model to track uploaded rate list PDFs."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=255, help_text="Name/description of the rate list")
    pdf_file = models.FileField(upload_to='rate_lists/', help_text="Upload PDF rate list")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_products = models.PositiveIntegerField(default=0, help_text="Total products found in PDF")
    imported_products = models.PositiveIntegerField(default=0, help_text="Products successfully imported")
    errors = models.JSONField(default=list, blank=True, help_text="Processing errors")
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='uploaded_rate_lists')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Rate List Upload'
        verbose_name_plural = 'Rate List Uploads'
    
    def __str__(self):
        return f"{self.name} - {self.status}"
    
    @property
    def success_rate(self):
        """Calculate success rate of import."""
        if self.total_products == 0:
            return 0
        return (self.imported_products / self.total_products) * 100


class RegulatedProduct(models.Model):
    """Products regulated by government with official prices."""
    
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100)
    gov_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50, default='piece')  # piece, kg, liter, etc.
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - ${self.gov_price}"
    
    @property
    def price_violation_threshold(self):
        """Calculate 10% above government price as violation threshold."""
        return self.gov_price * 1.10
