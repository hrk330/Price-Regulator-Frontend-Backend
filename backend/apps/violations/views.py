from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Max, Sum
from django.db import models
from django.utils import timezone

from .models import Violation, ViolationCheckReport
from .serializers import ViolationSerializer, ViolationUpdateSerializer
from apps.cases.models import Case


class ViolationListView(generics.ListAPIView):
    """List violations with filtering."""
    
    serializer_class = ViolationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Violation.objects.select_related(
            'regulated_product', 'scraped_product', 'confirmed_by'
        ).prefetch_related(
            'case__case_notes__author'
        ).all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by product
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(regulated_product_id=product_id)
        
        # Filter by violation type
        violation_type = self.request.query_params.get('violation_type')
        if violation_type:
            queryset = queryset.filter(violation_type=violation_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset


class ViolationDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update a violation."""
    
    queryset = Violation.objects.select_related(
        'regulated_product', 'scraped_product', 'confirmed_by'
    ).all()
    serializer_class = ViolationUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ViolationSerializer
        return ViolationUpdateSerializer
    
    def perform_update(self, serializer):
        # Only investigators can update violations
        if not self.request.user.is_investigator:
            raise permissions.PermissionDenied("Only investigators can update violations.")
        
        violation = self.get_object()
        
        # If confirming violation, create a case
        if serializer.validated_data.get('status') == 'confirmed':
            violation.confirmed_by = self.request.user
            violation.confirmed_at = timezone.now()
            violation.save()
            
            # Create case if it doesn't exist
            if not Case.objects.filter(violation=violation).exists():
                Case.objects.create(
                    violation=violation,
                    investigator=self.request.user,
                    status='open',
                    notes=f"Case created from confirmed violation: {violation.violation_type}"
                )
        
        serializer.save()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_violation_view(request, violation_id):
    """Confirm a violation and create a case."""
    
    if not request.user.is_investigator:
        return Response(
            {'error': 'Only investigators can confirm violations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        violation = Violation.objects.get(id=violation_id)
        
        if violation.status != 'pending':
            return Response(
                {'error': 'Violation is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update violation
        violation.status = 'confirmed'
        violation.confirmed_by = request.user
        violation.confirmed_at = timezone.now()
        violation.save()
        
        # Create case
        case, created = Case.objects.get_or_create(
            violation=violation,
            defaults={
                'investigator': request.user,
                'status': 'open',
                'notes': f"Case created from confirmed violation: {violation.violation_type}"
            }
        )
        
        return Response({
            'message': 'Violation confirmed and case created',
            'violation_id': violation.id,
            'case_id': case.id,
            'case_created': created
        })
        
    except Violation.DoesNotExist:
        return Response(
            {'error': 'Violation not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def dismiss_violation_view(request, violation_id):
    """Dismiss a violation."""
    
    if not request.user.is_investigator:
        return Response(
            {'error': 'Only investigators can dismiss violations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        violation = Violation.objects.get(id=violation_id)
        
        if violation.status != 'pending':
            return Response(
                {'error': 'Violation is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        violation.status = 'dismissed'
        violation.confirmed_by = request.user
        violation.confirmed_at = timezone.now()
        violation.save()
        
        return Response({
            'message': 'Violation dismissed',
            'violation_id': violation.id
        })
        
    except Violation.DoesNotExist:
        return Response(
            {'error': 'Violation not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def violation_stats_view(request):
    """Get violation statistics."""
    
    # Total violations
    total_violations = Violation.objects.count()
    
    # Violations by status
    status_stats = Violation.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Violations by severity
    severity_stats = Violation.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('severity')
    
    # Recent violations (last 7 days)
    recent_violations = Violation.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    # Pending violations
    pending_violations = Violation.objects.filter(status='pending').count()
    
    return Response({
        'total_violations': total_violations,
        'status_stats': list(status_stats),
        'severity_stats': list(severity_stats),
        'recent_violations': recent_violations,
        'pending_violations': pending_violations,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def full_violation_report_view(request):
    """Get comprehensive violation report with all product comparisons."""
    
    from django.core.cache import cache
    
    # Try to get cached report first
    cache_key = 'full_violation_report'
    cached_report = cache.get(cache_key)
    
    if cached_report:
        return Response(cached_report)
    
    # Get all violation check reports with optimized queries
    reports = ViolationCheckReport.objects.select_related(
        'regulated_product', 'scraped_product'
    ).prefetch_related(
        'violation_record'
    ).all()
    
    # Basic statistics
    total_reports = reports.count()
    violations_found = reports.filter(has_violation=True).count()
    compliant_products = reports.filter(compliance_status='ok').count()
    no_matches = reports.filter(compliance_status='no_match').count()
    
    # Violation severity breakdown
    severity_stats = reports.filter(has_violation=True).values('violation_severity').annotate(
        count=Count('id')
    ).order_by('violation_severity')
    
    # Marketplace breakdown
    marketplace_stats = reports.values('scraped_product__marketplace').annotate(
        total=Count('id'),
        violations=Count('id', filter=Q(has_violation=True)),
        compliant=Count('id', filter=Q(compliance_status='ok')),
        no_match=Count('id', filter=Q(compliance_status='no_match'))
    ).order_by('scraped_product__marketplace')
    
    # Top violating products
    top_violators = reports.filter(has_violation=True).order_by('-percentage_difference')[:10]
    top_violators_data = []
    for report in top_violators:
        top_violators_data.append({
            'scraped_product': report.scraped_product.product_name,
            'marketplace': report.marketplace,
            'regulated_product': report.regulated_product.name if report.regulated_product else 'N/A',
            'scraped_price': float(report.scraped_price),
            'regulated_price': float(report.regulated_price) if report.regulated_price else None,
            'percentage_over': float(report.percentage_difference) if report.percentage_difference else 0,
            'severity': report.violation_severity,
            'proposed_penalty': float(report.proposed_penalty) if report.proposed_penalty else None,
        })
    
    # Price statistics
    violation_reports = reports.filter(has_violation=True)
    if violation_reports.exists():
        avg_violation_percentage = violation_reports.aggregate(
            avg_pct=models.Avg('percentage_difference')
        )['avg_pct'] or 0
        
        max_violation_percentage = violation_reports.aggregate(
            max_pct=models.Max('percentage_difference')
        )['max_pct'] or 0
        
        total_penalty_amount = violation_reports.aggregate(
            total_penalty=models.Sum('proposed_penalty')
        )['total_penalty'] or 0
    else:
        avg_violation_percentage = 0
        max_violation_percentage = 0
        total_penalty_amount = 0
    
    # Recent activity (last 7 days)
    recent_reports = reports.filter(
        check_date__gte=timezone.now() - timezone.timedelta(days=7)
    )
    recent_violations = recent_reports.filter(has_violation=True).count()
    recent_compliant = recent_reports.filter(compliance_status='ok').count()
    
    report_data = {
        'summary': {
            'total_products_checked': total_reports,
            'violations_found': violations_found,
            'compliant_products': compliant_products,
            'no_matching_regulated_product': no_matches,
            'violation_rate': round((violations_found / total_reports * 100), 2) if total_reports > 0 else 0,
        },
        'violation_breakdown': {
            'by_severity': list(severity_stats),
            'by_marketplace': list(marketplace_stats),
        },
        'price_statistics': {
            'average_violation_percentage': round(float(avg_violation_percentage), 2),
            'maximum_violation_percentage': round(float(max_violation_percentage), 2),
            'total_proposed_penalties': round(float(total_penalty_amount), 2),
        },
        'top_violators': top_violators_data,
        'recent_activity': {
            'last_7_days_violations': recent_violations,
            'last_7_days_compliant': recent_compliant,
        },
        'generated_at': timezone.now().isoformat(),
    }
    
    # Cache the report for 5 minutes
    cache.set(cache_key, report_data, 300)
    
    return Response(report_data)
