from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
import uuid

from .models import UserSession
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    UserSessionSerializer, RefreshTokenSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with session tracking."""
    
    permission_classes = []  # No authentication required for login
    authentication_classes = []  # No authentication required for login
    
    def post(self, request, *args, **kwargs):
        # Debug: Print what we're receiving
        print(f"DEBUG: Request data: {request.data}")
        print(f"DEBUG: Request META: {request.META.get('CONTENT_TYPE')}")
        print(f"DEBUG: Request method: {request.method}")
        
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Serializer errors: {serializer.errors}")
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        device_id = serializer.validated_data['device_id']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Get client info
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create or update session
        with transaction.atomic():
            session, created = UserSession.objects.update_or_create(
                user=user,
                device_id=device_id,
                defaults={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'expires_at': timezone.now() + timezone.timedelta(days=7),
                    'is_active': True,
                }
            )
        
        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': UserSerializer(user).data,
            'session_id': str(session.id),
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user and revoke session."""
    try:
        device_id = request.data.get('device_id')
        if device_id:
            UserSession.objects.filter(
                user=request.user,
                device_id=device_id
            ).update(is_active=False)
        
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([])  # No authentication required for token refresh
def refresh_token_view(request):
    """Refresh access token."""
    serializer = RefreshTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    refresh_token = serializer.validated_data['refresh_token']
    device_id = serializer.validated_data['device_id']
    
    try:
        # Find the session
        session = UserSession.objects.get(
            refresh_token=refresh_token,
            device_id=device_id,
            is_active=True
        )
        
        if session.is_expired:
            session.is_active = False
            session.save()
            return Response(
                {'error': 'Session expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate new tokens
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)
        new_refresh_token = str(refresh)
        
        # Update session
        session.access_token = new_access_token
        session.refresh_token = new_refresh_token
        session.expires_at = timezone.now() + timezone.timedelta(days=7)
        session.save()
        
        return Response({
            'access': new_access_token,
            'refresh': new_refresh_token,
        })
        
    except UserSession.DoesNotExist:
        return Response(
            {'error': 'Invalid session'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    """Get current user information."""
    return Response(UserSerializer(request.user).data)


class UserSessionListView(generics.ListAPIView):
    """List active sessions for admin users."""
    
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return UserSession.objects.filter(is_active=True)
        return UserSession.objects.filter(user=self.request.user, is_active=True)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def revoke_session_view(request, session_id):
    """Revoke a specific session."""
    try:
        session = UserSession.objects.get(id=session_id)
        
        # Only allow users to revoke their own sessions, or admins to revoke any
        if not (session.user == request.user or request.user.is_admin):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session.is_active = False
        session.save()
        
        return Response({'message': 'Session revoked successfully'})
        
    except UserSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
