from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRequirementViewSet, AdminRequirementViewSet, AttachmentDownloadView, UserListView, UserCreateView, ReviewSessionView, ReviewMessageView, ReviewSessionConfirmView, ReviewSessionDiscardView, AdminReviewSessionsView

router = DefaultRouter()
router.register(r'requests', UserRequirementViewSet, basename='user-requests')
router.register(r'admin/requests', AdminRequirementViewSet, basename='admin-requests')

urlpatterns = [
    path('', include(router.urls)),
    path('attachments/<int:pk>/download/', AttachmentDownloadView.as_view(), name='attachment-download'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('admin/users/', UserCreateView.as_view(), name='user-create'),
    path('ai/review-sessions/', ReviewSessionView.as_view(), name='review-session-create'),
    path('ai/review-sessions/<int:session_id>/messages/', ReviewMessageView.as_view(), name='review-session-messages'),
    path('ai/review-sessions/<int:session_id>/confirm/', ReviewSessionConfirmView.as_view(), name='review-session-confirm'),
    path('ai/review-sessions/<int:session_id>/discard/', ReviewSessionDiscardView.as_view(), name='review-session-discard'),
    path('admin/requests/<int:requirement_id>/review-sessions/', AdminReviewSessionsView.as_view(), name='admin-review-sessions'),
]
