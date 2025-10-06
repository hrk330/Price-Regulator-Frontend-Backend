from rest_framework import serializers
from .models import Case, CaseNote
from apps.violations.serializers import ViolationSerializer
from apps.accounts.serializers import UserSerializer


class CaseNoteSerializer(serializers.ModelSerializer):
    """Serializer for CaseNote model."""
    
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = CaseNote
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class CaseSerializer(serializers.ModelSerializer):
    """Serializer for Case model."""
    
    violation = ViolationSerializer(read_only=True)
    investigator = UserSerializer(read_only=True)
    case_notes = CaseNoteSerializer(many=True, read_only=True)
    
    class Meta:
        model = Case
        fields = [
            'id', 'violation', 'investigator', 'status', 'notes',
            'resolution_notes', 'final_penalty', 'closed_at',
            'created_at', 'updated_at', 'case_notes'
        ]
        read_only_fields = [
            'id', 'violation', 'investigator', 'closed_at',
            'created_at', 'updated_at', 'case_notes'
        ]


class CaseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a case."""
    
    class Meta:
        model = Case
        fields = ['violation', 'notes']
    
    def validate_violation(self, value):
        if value.status != 'confirmed':
            raise serializers.ValidationError("Can only create cases for confirmed violations.")
        return value


class CaseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a case."""
    
    class Meta:
        model = Case
        fields = ['status', 'notes', 'resolution_notes', 'final_penalty']
    
    def validate_status(self, value):
        if value == 'closed' and not self.instance.resolution_notes:
            raise serializers.ValidationError("Resolution notes are required when closing a case.")
        return value


class CaseNoteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating case notes."""
    
    class Meta:
        model = CaseNote
        fields = ['content']
