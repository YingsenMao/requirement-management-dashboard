from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import F
from .models import RequirementRequest
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
        # Sort by priority score descending, nulls last, then by submission date descending
        return RequirementRequest.objects.all().order_by(F('priority_score').desc(nulls_last=True), '-submission_date')

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
        # Admins see all requests, sorted by priority score descending, nulls last
        return RequirementRequest.objects.all().order_by(F('priority_score').desc(nulls_last=True))
