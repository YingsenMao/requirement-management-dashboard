import os
import mimetypes
from urllib.parse import quote
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.db.models import F, Case, When, Value, IntegerField
from django.http import FileResponse, Http404
from .models import RequirementRequest, Attachment, CustomUser
from .serializers import RequirementRequestSerializer, AdminRequirementSerializer
from .permissions import IsOwnerAndPendingReview, IsAdminUser

class UserRequirementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for regular users to view all requirements, 
    but only manage their own requirement requests.
    """
    serializer_class = RequirementRequestSerializer
    permission_classes = [IsAuthenticated, IsOwnerAndPendingReview]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Users can view all requests (Global Read), but permissions will restrict editing
        # Sort by: 1. Completed status at the bottom, 2. Priority score descending (nulls last), 3. Submission date descending
        return RequirementRequest.objects.annotate(
            is_completed=Case(
                When(status='completed', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('is_completed', F('priority_score').desc(nulls_last=True), '-submission_date')

    def perform_create(self, serializer):
        # Automatically assign the current user as the submitter
        serializer.save(submitter=self.request.user)

class AdminRequirementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admins to view and manage all requirement requests.
    """
    serializer_class = AdminRequirementSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # Admins see all requests, sorted with completed at the bottom, then by priority score descending (nulls last)
        return RequirementRequest.objects.annotate(
            is_completed=Case(
                When(status='completed', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('is_completed', F('priority_score').desc(nulls_last=True), '-submission_date')


class UserListView(APIView):
    """
    Returns a list of all regular users (for the Submitter filter).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.filter(role='user').values('id', 'username')
        return Response(list(users))


class AttachmentDownloadView(APIView):
    """
    Secure endpoint to download attachments.
    Ensures only the submitter or an admin can download the file.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            attachment = Attachment.objects.select_related('requirement__submitter').get(pk=pk)
        except Attachment.DoesNotExist:
            raise Http404("Attachment not found")

        requirement = attachment.requirement
        user = request.user

        # Defensive Permission Check: Admin or Submitter
        is_admin = getattr(user, 'role', None) == 'admin'
        is_submitter = requirement.submitter_id == user.id

        if not (is_admin or is_submitter):
            return Response({"detail": "You do not have permission to download this file."}, status=403)

        file_path = attachment.file.path
        if not os.path.exists(file_path):
            raise Http404("File not found on server")

        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

        # FileResponse handles streaming and sets appropriate headers
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        
        # Set Content-Disposition to trigger download in browser
        file_name = os.path.basename(attachment.file.name)
        encoded_name = quote(file_name)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_name}"
        
        return response
