from rest_framework import permissions


class IsAdminOrViewOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        anonymous (unauthenticated) users have  a GET access to the view,
        However, for other operations, users must be an admin
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
