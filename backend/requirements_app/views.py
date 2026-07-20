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
    pagination_class = None

    def get_queryset(self):
        return RequirementRequest.objects.select_related('submitter').prefetch_related('attachments').annotate(
            is_completed=Case(
                When(status='completed', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('is_completed', F('priority_score').desc(nulls_last=True), '-submission_date')

    def perform_create(self, serializer):
        serializer.save(submitter=self.request.user)

    def perform_update(self, serializer):
        if self.get_object().status == 'rejected':
            serializer.save(status='pending_review', reject_reason=None)
        else:
            serializer.save()

class AdminRequirementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admins to view and manage all requirement requests.
    """
    serializer_class = AdminRequirementSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None

    def get_queryset(self):
        return RequirementRequest.objects.select_related('submitter').prefetch_related('attachments').annotate(
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

        file_handle = open(file_path, 'rb')
        response = FileResponse(file_handle, content_type=content_type)

        file_name = os.path.basename(attachment.file.name)
        encoded_name = quote(file_name)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_name}"

        return response
