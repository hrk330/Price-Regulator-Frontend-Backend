from django.urls import path
from .views import summary_report_view, export_csv_view, dashboard_metrics_view

urlpatterns = [
    path('summary/', summary_report_view, name='report_summary'),
    path('export/', export_csv_view, name='export_csv'),
    path('dashboard-metrics/', dashboard_metrics_view, name='dashboard_metrics'),
]
