from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser
    
class IsSalesUser(BasePermission):
    """
    Allow only Sales group members or superusers.
    """
    message = "Only Sales users can perform this action."

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if u.is_superuser:
            return True
        return u.groups.filter(name__iexact="Sales").exists()