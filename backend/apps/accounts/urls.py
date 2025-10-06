from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    CustomTokenObtainPairView, logout_view, refresh_token_view,
    me_view, UserSessionListView, revoke_session_view
)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', logout_view, name='logout'),
    path('refresh/', refresh_token_view, name='token_refresh'),
    path('me/', me_view, name='me'),
]
