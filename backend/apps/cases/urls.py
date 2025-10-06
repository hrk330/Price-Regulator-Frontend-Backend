from django.urls import path
from .views import (
    CaseListCreateView, CaseDetailView, CaseNoteListCreateView,
    case_stats_view, close_case_view
)

urlpatterns = [
    path('', CaseListCreateView.as_view(), name='case_list_create'),
    path('<int:pk>/', CaseDetailView.as_view(), name='case_detail'),
    path('<int:case_id>/notes/', CaseNoteListCreateView.as_view(), name='case_notes'),
    path('<int:case_id>/close/', close_case_view, name='close_case'),
    path('stats/', case_stats_view, name='case_stats'),
]
