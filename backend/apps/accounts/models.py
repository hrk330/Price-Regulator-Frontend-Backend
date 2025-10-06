from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """Custom User model with role-based access control."""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('investigator', 'Investigator'),
        ('regulator', 'Regulator'),
    ]
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='investigator')
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_investigator(self):
        return self.role == 'investigator'
    
    @property
    def is_regulator(self):
        return self.role == 'regulator'


class UserSession(models.Model):
    """Track user sessions across multiple devices."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    device_id = models.CharField(max_length=255, help_text="Unique identifier for the device")
    access_token = models.TextField()
    refresh_token = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'device_id']
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.name} - {self.device_id}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
