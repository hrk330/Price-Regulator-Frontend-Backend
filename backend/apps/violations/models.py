from django.db import models
from django.core.validators import MinValueValidator


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
