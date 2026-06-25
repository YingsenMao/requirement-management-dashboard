from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'admin' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class IsOwnerAndPendingReview(permissions.BasePermission):
    """
    Custom permission:
    - Read access: Any authenticated user (Global Read).
    - Write/Delete access: Only the owner, and only if status is 'pending_review'.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write/Delete permissions are only allowed to the owner if status is pending_review
        return obj.submitter == request.user and obj.status == 'pending_review'
