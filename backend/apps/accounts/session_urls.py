from django.urls import path
from .views import UserSessionListView, revoke_session_view

urlpatterns = [
    path('', UserSessionListView.as_view(), name='session_list'),
    path('<uuid:session_id>/revoke/', revoke_session_view, name='revoke_session'),
]
