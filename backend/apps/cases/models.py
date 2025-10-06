from django.db import models
from django.utils import timezone


class Case(models.Model):
    """Investigation cases created from confirmed violations."""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('resolved', 'Resolved'),
    ]
    
    violation = models.OneToOneField(
        'violations.Violation',
        on_delete=models.CASCADE,
        related_name='case'
    )
    investigator = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='investigated_cases'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    notes = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    final_penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final penalty amount after investigation"
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'investigator']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Case #{self.id} - {self.violation.regulated_product.name}"
    
    def close_case(self, resolution_notes="", final_penalty=None):
        """Close the case with resolution details."""
        self.status = 'closed'
        self.resolution_notes = resolution_notes
        self.final_penalty = final_penalty
        self.closed_at = timezone.now()
        self.save()


class CaseNote(models.Model):
    """Notes and updates for cases."""
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='case_notes'
    )
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='case_notes'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for Case #{self.case.id} by {self.author.name}"
