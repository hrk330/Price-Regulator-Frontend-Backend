"""
Middleware to handle automatic logout when UserSession is deactivated.
"""

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
import hashlib

from .models import UserSession


class UserSessionMiddleware(MiddlewareMixin):
    """
    Middleware to check if the current user's session is still active.
    If the session is deactivated in admin, automatically log out the user.
    """
    
    def process_request(self, request):
        """Check session status on each request."""
        # Only check for authenticated users
        if not request.user.is_authenticated:
            return None
            
        # Skip checking for API requests (they use JWT tokens)
        if request.path.startswith('/api/'):
            return None
            
        # Skip checking for admin logout to avoid redirect loops
        if request.path == '/admin/logout/':
            return None
            
        try:
            # Generate device ID for the current request (same logic as in signals.py)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            ip_address = self.get_client_ip(request)
            device_info = f"{user_agent}_{ip_address}_{request.user.id}"
            device_id = hashlib.md5(device_info.encode()).hexdigest()[:32]
            
            # Check if there's an active session for this user and device
            session = UserSession.objects.filter(
                user=request.user,
                device_id=device_id,
                is_active=True
            ).first()
            
            # If no active session found, log out the user
            if not session:
                logout(request)
                # Redirect to login with a message parameter
                return redirect('/admin/login/?message=session_deactivated')
                
        except Exception as e:
            # If there's any error, don't break the request
            print(f"Error in UserSessionMiddleware: {e}")
            pass
            
        return None
    
    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
