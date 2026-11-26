from rest_framework import permissions

from .access import is_owner


class IsOwnerPermission(permissions.BasePermission):
    """Allow access only to authenticated owner/superuser accounts."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_owner(request.user))


class IsOwnerOrReadOnlyPermission(permissions.BasePermission):
    """Allow read-only access to authenticated users and write access only to owners."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_owner(request.user)
