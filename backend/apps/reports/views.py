from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv
import io

from apps.products.models import RegulatedProduct
from apps.violations.models import Violation
from apps.cases.models import Case
from apps.scraping.models import ScrapedProduct


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def summary_report_view(request):
    """Get summary report with key metrics."""
    
    # Only regulators and admins can access reports
    if not (request.user.is_regulator or request.user.is_admin):
        return Response(
            {'error': 'Only regulators and admins can access reports'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Date range filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base querysets
    products_qs = RegulatedProduct.objects.filter(is_active=True)
    violations_qs = Violation.objects.all()
    cases_qs = Case.objects.all()
    scraped_qs = ScrapedProduct.objects.all()
    
    # Apply date filters
    if date_from:
        violations_qs = violations_qs.filter(created_at__date__gte=date_from)
        cases_qs = cases_qs.filter(created_at__date__gte=date_from)
        scraped_qs = scraped_qs.filter(scraped_at__date__gte=date_from)
    
    if date_to:
        violations_qs = violations_qs.filter(created_at__date__lte=date_to)
        cases_qs = cases_qs.filter(created_at__date__lte=date_to)
        scraped_qs = scraped_qs.filter(scraped_at__date__lte=date_to)
    
    # Calculate metrics
    total_products = products_qs.count()
    total_violations = violations_qs.count()
    total_cases = cases_qs.count()
    total_penalties = violations_qs.aggregate(
        total=Sum('proposed_penalty')
    )['total'] or 0
    
    # Violations by severity
    violations_by_severity = dict(
        violations_qs.values('severity').annotate(
            count=Count('id')
        ).values_list('severity', 'count')
    )
    
    # Violations by status
    violations_by_status = dict(
        violations_qs.values('status').annotate(
            count=Count('id')
        ).values_list('status', 'count')
    )
    
    # Cases by status
    cases_by_status = dict(
        cases_qs.values('status').annotate(
            count=Count('id')
        ).values_list('status', 'count')
    )
    
    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_violations = Violation.objects.filter(created_at__gte=week_ago).count()
    recent_cases = Case.objects.filter(created_at__gte=week_ago).count()
    recent_scraped = ScrapedProduct.objects.filter(scraped_at__gte=week_ago).count()
    
    recent_activity = {
        'violations': recent_violations,
        'cases': recent_cases,
        'scraped_products': recent_scraped
    }
    
    return Response({
        'total_products': total_products,
        'total_violations': total_violations,
        'total_cases': total_cases,
        'total_penalties': float(total_penalties),
        'violations_by_severity': violations_by_severity,
        'violations_by_status': violations_by_status,
        'cases_by_status': cases_by_status,
        'recent_activity': recent_activity
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_csv_view(request):
    """Export data as CSV."""
    
    if not (request.user.is_regulator or request.user.is_admin):
        return Response(
            {'error': 'Only regulators and admins can export data'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    export_type = request.GET.get('type', 'violations')
    
    if export_type == 'violations':
        return export_violations_csv()
    elif export_type == 'cases':
        return export_cases_csv()
    elif export_type == 'products':
        return export_products_csv()
    else:
        return Response(
            {'error': 'Invalid export type'},
            status=status.HTTP_400_BAD_REQUEST
        )


def export_violations_csv():
    """Export violations data as CSV."""
    
    violations = Violation.objects.select_related(
        'regulated_product', 'scraped_product', 'confirmed_by'
    ).all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="violations_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Product Name', 'Marketplace', 'Listed Price', 'Government Price',
        'Price Difference', 'Percentage Over', 'Violation Type', 'Severity',
        'Proposed Penalty', 'Status', 'Confirmed By', 'Created At'
    ])
    
    for violation in violations:
        writer.writerow([
            violation.id,
            violation.regulated_product.name,
            violation.scraped_product.marketplace,
            violation.scraped_product.listed_price,
            violation.regulated_product.gov_price,
            violation.price_difference,
            f"{violation.percentage_over:.2f}%",
            violation.violation_type,
            violation.severity,
            violation.proposed_penalty,
            violation.status,
            violation.confirmed_by.name if violation.confirmed_by else '',
            violation.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


def export_cases_csv():
    """Export cases data as CSV."""
    
    cases = Case.objects.select_related(
        'violation__regulated_product', 'investigator'
    ).all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="cases_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Case ID', 'Product Name', 'Investigator', 'Status', 'Final Penalty',
        'Resolution Notes', 'Created At', 'Closed At'
    ])
    
    for case in cases:
        writer.writerow([
            case.id,
            case.violation.regulated_product.name,
            case.investigator.name,
            case.status,
            case.final_penalty or '',
            case.resolution_notes,
            case.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            case.closed_at.strftime('%Y-%m-%d %H:%M:%S') if case.closed_at else ''
        ])
    
    return response


def export_products_csv():
    """Export regulated products data as CSV."""
    
    products = RegulatedProduct.objects.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="products_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Name', 'Category', 'Government Price', 'Unit', 'Description',
        'Is Active', 'Created At'
    ])
    
    for product in products:
        writer.writerow([
            product.id,
            product.name,
            product.category,
            product.gov_price,
            product.unit,
            product.description,
            product.is_active,
            product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_metrics_view(request):
    """Get dashboard metrics for charts and KPIs."""
    
    if not (request.user.is_regulator or request.user.is_admin):
        return Response(
            {'error': 'Only regulators and admins can access dashboard metrics'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Time series data for violations (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    violations_timeline = []
    
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        count = Violation.objects.filter(
            created_at__date=date.date()
        ).count()
        violations_timeline.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Top violating products
    top_violating_products = list(
        Violation.objects.values('regulated_product__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Violations by marketplace
    violations_by_marketplace = dict(
        Violation.objects.values('scraped_product__marketplace')
        .annotate(count=Count('id'))
        .values_list('scraped_product__marketplace', 'count')
    )
    
    # Average penalty by severity
    avg_penalty_by_severity = dict(
        Violation.objects.values('severity')
        .annotate(avg_penalty=Sum('proposed_penalty') / Count('id'))
        .values_list('severity', 'avg_penalty')
    )
    
    return Response({
        'violations_timeline': violations_timeline,
        'top_violating_products': top_violating_products,
        'violations_by_marketplace': violations_by_marketplace,
        'avg_penalty_by_severity': avg_penalty_by_severity
    })
