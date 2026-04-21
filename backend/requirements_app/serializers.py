from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.dateparse import parse_date, parse_datetime
from .models import RequirementRequest, CustomUser

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the token payload
        token['role'] = user.role
        token['username'] = user.username
        return token

class RequirementRequestSerializer(serializers.ModelSerializer):
    submitter_username = serializers.CharField(source='submitter.username', read_only=True)
    # Explicitly mark optional fields to prevent validation errors when omitted or sent as null/empty
    # allow_blank=True is critical to accept empty strings from frontend date pickers
    deadline = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    supplementary_materials = serializers.JSONField(required=False, allow_null=True, default=list)
    revenue_impact = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    
    class Meta:
        model = RequirementRequest
        fields = [
            'id', 'name', 'summary', 'region', 'requirement_type', 
            'impacted_users', 'supplementary_materials', 'revenue_impact', 
            'deadline', 'submission_date', 'workload', 'status', 
            'priority_score', 'submitter', 'submitter_username'
        ]
        read_only_fields = ['id', 'submission_date', 'priority_score', 'submitter', 'submitter_username']

    def validate_deadline(self, value):
        if value is None or value == '':
            return None
        # Try parsing as standard date (YYYY-MM-DD)
        parsed = parse_date(str(value))
        if parsed:
            return parsed
        # Try parsing as ISO datetime (e.g., 2023-10-25T00:00:00.000Z) and extract date
        parsed_dt = parse_datetime(str(value))
        if parsed_dt:
            return parsed_dt.date()
        raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD or ISO 8601.")
