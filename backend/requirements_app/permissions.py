from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'admin' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class IsOwnerAndPendingReview(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it,
    and only if the object's status is 'pending_review'.
    Read access is allowed to the owner regardless of status.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to the owner
        if request.method in permissions.SAFE_METHODS:
            return obj.submitter == request.user
        
        # Write permissions are only allowed to the owner if status is pending_review
        return obj.submitter == request.user and obj.status == 'pending_review'
