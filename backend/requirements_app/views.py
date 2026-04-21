from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import RequirementRequest
from .serializers import RequirementRequestSerializer
from .permissions import IsOwnerAndPendingReview, IsAdminUser

class UserRequirementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for regular users to manage their own requirement requests.
    """
    serializer_class = RequirementRequestSerializer
    permission_classes = [IsAuthenticated, IsOwnerAndPendingReview]

    def get_queryset(self):
        # Users can only see their own requests
        return RequirementRequest.objects.filter(submitter=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the current user as the submitter
        serializer.save(submitter=self.request.user)

class AdminRequirementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admins to view and manage all requirement requests.
    """
    serializer_class = RequirementRequestSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Admins see all requests, sorted by priority score descending
        return RequirementRequest.objects.all().order_by('-priority_score')
