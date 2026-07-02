from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRequirementViewSet, AdminRequirementViewSet, AttachmentDownloadView, UserListView

router = DefaultRouter()
router.register(r'requests', UserRequirementViewSet, basename='user-requests')
router.register(r'admin/requests', AdminRequirementViewSet, basename='admin-requests')

urlpatterns = [
    path('', include(router.urls)),
    path('attachments/<int:pk>/download/', AttachmentDownloadView.as_view(), name='attachment-download'),
    path('users/', UserListView.as_view(), name='user-list'),
]
