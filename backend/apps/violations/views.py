from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone

from .models import Violation
from .serializers import ViolationSerializer, ViolationUpdateSerializer
from apps.cases.models import Case


class ViolationListView(generics.ListAPIView):
    """List violations with filtering."""
    
    serializer_class = ViolationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Violation.objects.select_related(
            'regulated_product', 'scraped_product', 'confirmed_by'
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
