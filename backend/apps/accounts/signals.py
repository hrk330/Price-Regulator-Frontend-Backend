"""
Signal handlers for user authentication events.
This module tracks both API and Django admin logins to create UserSession records.
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
import uuid
import hashlib

from .models import UserSession


@receiver(user_logged_in)
def create_user_session_on_login(sender, request, user, **kwargs):
    """
    Create a UserSession record when a user logs in through Django admin or any other method.
    This ensures all logins are tracked in the UserSession model.
    """
    try:
        # Generate a device ID based on user agent and IP for Django admin logins
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = get_client_ip(request)
        
        # Create a unique device ID for Django admin sessions
        device_info = f"{user_agent}_{ip_address}_{user.id}"
        device_id = hashlib.md5(device_info.encode()).hexdigest()[:32]
        
        # For Django admin logins, we don't have JWT tokens, so we'll use placeholder values
        # and mark the session as an admin session
        with transaction.atomic():
            session, created = UserSession.objects.update_or_create(
                user=user,
                device_id=device_id,
                defaults={
                    'session_type': 'admin',
                    'access_token': f"admin_session_{uuid.uuid4()}",  # Placeholder for admin sessions
                    'refresh_token': f"admin_refresh_{uuid.uuid4()}",  # Placeholder for admin sessions
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'expires_at': timezone.now() + timezone.timedelta(days=7),
                    'is_active': True,
                }
            )
            
            if created:
                print(f"Created UserSession for Django admin login: {user.email} from {ip_address}")
            else:
                print(f"Updated UserSession for Django admin login: {user.email} from {ip_address}")
                
    except Exception as e:
        print(f"Error creating UserSession for Django admin login: {e}")


@receiver(user_logged_out)
def deactivate_user_session_on_logout(sender, request, user, **kwargs):
    """
    Deactivate UserSession records when a user logs out.
    """
    try:
        # Get client info to find the session
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = get_client_ip(request)
        
        # Create the same device ID as used in login
        device_info = f"{user_agent}_{ip_address}_{user.id}"
        device_id = hashlib.md5(device_info.encode()).hexdigest()[:32]
        
        # Deactivate the session
        UserSession.objects.filter(
            user=user,
            device_id=device_id,
            is_active=True
        ).update(is_active=False)
        
        print(f"Deactivated UserSession for Django admin logout: {user.email}")
        
    except Exception as e:
        print(f"Error deactivating UserSession for Django admin logout: {e}")


def get_client_ip(request):
    """Get the client IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
