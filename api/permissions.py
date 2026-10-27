from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_admin(user):
    return bool(user and user.is_authenticated and (user.admin or user.is_staff))


# ==========================================
# CATALOGUE: Anyone can browse, only admins can change it
# ==========================================
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or is_admin(request.user)


# ==========================================
# ACCOUNTS: Users can only see and edit themselves
# ==========================================
class IsSelfOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj == request.user or is_admin(request.user)
