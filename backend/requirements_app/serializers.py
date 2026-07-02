import os
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.dateparse import parse_date, parse_datetime
from .models import RequirementRequest, CustomUser, Attachment

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the token payload
        token['role'] = user.role
        token['username'] = user.username
        return token

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class RequirementRequestSerializer(serializers.ModelSerializer):
    submitter_username = serializers.CharField(source='submitter.username', read_only=True)
    deadline = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    supplementary_materials = serializers.JSONField(required=False, allow_null=True, default=list)
    revenue_impact = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    impacted_users = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    
    # Renamed to 'uploaded_files' to avoid shadowing the 'attachments' related manager
    uploaded_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    attachments_list = AttachmentSerializer(source='attachments', many=True, read_only=True)
    
    # Changed to JSONField to correctly parse the JSON string sent from frontend FormData
    deleted_attachment_ids = serializers.JSONField(
        write_only=True,
        required=False,
        default=list
    )
    
    class Meta:
        model = RequirementRequest
        fields = [
            'id', 'name', 'summary', 'region', 'requirement_type', 
            'impacted_users', 'supplementary_materials', 'revenue_impact', 
            'deadline', 'submission_date', 'workload', 'status', 
            'priority_score', 'submitter', 'submitter_username',
            'uploaded_files', 'attachments_list', 'deleted_attachment_ids'
        ]
        read_only_fields = ['id', 'submission_date', 'priority_score', 'submitter', 'submitter_username']

    def validate_deadline(self, value):
        if value is None or value == '':
            return None
        parsed = parse_date(str(value))
        if parsed:
            return parsed
        parsed_dt = parse_datetime(str(value))
        if parsed_dt:
            return parsed_dt.date()
        raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD or ISO 8601.")

    def validate_uploaded_files(self, value):
        if not value:
            return value
        
        allowed_extensions = ['.pdf', '.docx', '.xlsx', '.png', '.jpg']
        
        for f in value:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(f"File type '{ext}' is not allowed. Allowed types: {', '.join(allowed_extensions)}")
            
            if f.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(f"File '{f.name}' exceeds the 5MB limit.")
            
        return value

    def validate(self, data):
        if self.instance:
            existing_count = self.instance.attachments.count()
            deleted_ids = data.get('deleted_attachment_ids', [])
            new_files = data.get('uploaded_files', [])
            
            valid_deleted_count = self.instance.attachments.filter(id__in=deleted_ids).count()
            final_count = existing_count - valid_deleted_count + len(new_files)
            
            if final_count > 3:
                raise serializers.ValidationError({"uploaded_files": "Maximum 3 files allowed in total."})
        else:
            new_files = data.get('uploaded_files', [])
            if len(new_files) > 3:
                raise serializers.ValidationError({"uploaded_files": "Maximum 3 files allowed."})
                
        return data

    def create(self, validated_data):
        attachments_data = validated_data.pop('uploaded_files', [])
        validated_data.pop('deleted_attachment_ids', None)
        requirement = super().create(validated_data)
        
        for f in attachments_data:
            Attachment.objects.create(requirement=requirement, file=f)
            
        return requirement

    def update(self, instance, validated_data):
        attachments_data = validated_data.pop('uploaded_files', None)
        deleted_attachment_ids = validated_data.pop('deleted_attachment_ids', [])
        
        instance = super().update(instance, validated_data)
        
        if deleted_attachment_ids:
            instance.attachments.filter(id__in=deleted_attachment_ids).delete()
            
        if attachments_data:
            for f in attachments_data:
                Attachment.objects.create(requirement=instance, file=f)
                
        return instance


class AdminRequirementSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for Admins assessing requirements.
    Restricts write access strictly to 'workload' and 'status'.
    """
    submitter_username = serializers.CharField(source='submitter.username', read_only=True)
    attachments_list = AttachmentSerializer(source='attachments', many=True, read_only=True)
    
    class Meta:
        model = RequirementRequest
        fields = [
            'id', 'name', 'summary', 'region', 'requirement_type', 
            'impacted_users', 'supplementary_materials', 'revenue_impact', 
            'deadline', 'submission_date', 'workload', 'status', 
            'priority_score', 'submitter', 'submitter_username', 'attachments_list'
        ]
        read_only_fields = [
            'id', 'name', 'summary', 'region', 'requirement_type', 
            'impacted_users', 'supplementary_materials', 'revenue_impact', 
            'deadline', 'submission_date', 'priority_score', 'submitter', 
            'submitter_username', 'attachments_list'
        ]
