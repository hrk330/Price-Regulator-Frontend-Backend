from rest_framework import serializers


class ReportSummarySerializer(serializers.Serializer):
    """Serializer for report summary data."""
    
    total_products = serializers.IntegerField()
    total_violations = serializers.IntegerField()
    total_cases = serializers.IntegerField()
    total_penalties = serializers.DecimalField(max_digits=10, decimal_places=2)
    violations_by_severity = serializers.DictField()
    violations_by_status = serializers.DictField()
    cases_by_status = serializers.DictField()
    recent_activity = serializers.DictField()
