from django.urls import path
from .views import (
    ViolationListView, ViolationDetailView, confirm_violation_view,
    dismiss_violation_view, violation_stats_view, full_violation_report_view
)

urlpatterns = [
    path('', ViolationListView.as_view(), name='violation_list'),
    path('<int:pk>/', ViolationDetailView.as_view(), name='violation_detail'),
    path('<int:violation_id>/confirm/', confirm_violation_view, name='confirm_violation'),
    path('<int:violation_id>/dismiss/', dismiss_violation_view, name='dismiss_violation'),
    path('stats/', violation_stats_view, name='violation_stats'),
    path('full-report/', full_violation_report_view, name='full_violation_report'),
]
