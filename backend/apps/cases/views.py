from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone

from .models import Case, CaseNote
from .serializers import (
    CaseSerializer, CaseCreateSerializer, CaseUpdateSerializer,
    CaseNoteSerializer, CaseNoteCreateSerializer
)


class CaseListCreateView(generics.ListCreateAPIView):
    """List and create cases."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CaseCreateSerializer
        return CaseSerializer
    
    def get_queryset(self):
        queryset = Case.objects.select_related(
            'violation__regulated_product',
            'violation__scraped_product',
            'investigator'
        ).prefetch_related('case_notes__author').all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by investigator
        investigator_id = self.request.query_params.get('investigator_id')
        if investigator_id:
            queryset = queryset.filter(investigator_id=investigator_id)
        
        # Filter by product
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(violation__regulated_product_id=product_id)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # If user is not admin, only show their cases
        if not self.request.user.is_admin:
            queryset = queryset.filter(investigator=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        # Only investigators can create cases
        if not self.request.user.is_investigator:
            raise permissions.PermissionDenied("Only investigators can create cases.")
        serializer.save(investigator=self.request.user)


class CaseDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update a case."""
    
    queryset = Case.objects.select_related(
        'violation__regulated_product',
        'violation__scraped_product',
        'investigator'
    ).prefetch_related('case_notes__author').all()
    serializer_class = CaseUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CaseSerializer
        return CaseUpdateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # If user is not admin, only show their cases
        if not self.request.user.is_admin:
            queryset = queryset.filter(investigator=self.request.user)
        return queryset
    
    def perform_update(self, serializer):
        case = self.get_object()
        
        # Only investigators can update cases
        if not self.request.user.is_investigator:
            raise permissions.PermissionDenied("Only investigators can update cases.")
        
        # If closing the case, set closed_at
        if serializer.validated_data.get('status') == 'closed':
            case.close_case(
                resolution_notes=serializer.validated_data.get('resolution_notes', ''),
                final_penalty=serializer.validated_data.get('final_penalty')
            )
        else:
            serializer.save()


class CaseNoteListCreateView(generics.ListCreateAPIView):
    """List and create case notes."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CaseNoteCreateSerializer
        return CaseNoteSerializer
    
    def get_queryset(self):
        case_id = self.kwargs['case_id']
        return CaseNote.objects.filter(case_id=case_id).select_related('author')
    
    def perform_create(self, serializer):
        case_id = self.kwargs['case_id']
        case = Case.objects.get(id=case_id)
        
        # Only investigators can add notes
        if not self.request.user.is_investigator:
            raise permissions.PermissionDenied("Only investigators can add case notes.")
        
        serializer.save(case=case, author=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def case_stats_view(request):
    """Get case statistics."""
    
    # Total cases
    total_cases = Case.objects.count()
    
    # Cases by status
    status_stats = Case.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Cases by investigator
    investigator_stats = Case.objects.values('investigator__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent cases (last 7 days)
    recent_cases = Case.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    # Open cases
    open_cases = Case.objects.filter(status__in=['open', 'in_progress']).count()
    
    # If user is not admin, filter by their cases
    if not request.user.is_admin:
        total_cases = Case.objects.filter(investigator=request.user).count()
        status_stats = Case.objects.filter(investigator=request.user).values('status').annotate(
            count=Count('id')
        ).order_by('status')
        recent_cases = Case.objects.filter(
            investigator=request.user,
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        open_cases = Case.objects.filter(
            investigator=request.user,
            status__in=['open', 'in_progress']
        ).count()
        investigator_stats = []
    
    return Response({
        'total_cases': total_cases,
        'status_stats': list(status_stats),
        'investigator_stats': list(investigator_stats),
        'recent_cases': recent_cases,
        'open_cases': open_cases,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def close_case_view(request, case_id):
    """Close a case with resolution details."""
    
    if not request.user.is_investigator:
        return Response(
            {'error': 'Only investigators can close cases'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        case = Case.objects.get(id=case_id)
        
        if case.investigator != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You can only close your own cases'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if case.status == 'closed':
            return Response(
                {'error': 'Case is already closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resolution_notes = request.data.get('resolution_notes', '')
        final_penalty = request.data.get('final_penalty')
        
        case.close_case(resolution_notes, final_penalty)
        
        return Response({
            'message': 'Case closed successfully',
            'case_id': case.id
        })
        
    except Case.DoesNotExist:
        return Response(
            {'error': 'Case not found'},
            status=status.HTTP_404_NOT_FOUND
        )
