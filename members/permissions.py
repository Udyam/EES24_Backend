from rest_framework.permissions import BasePermission

class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        # Your custom logic to determine permission
        # Return True if the user should have access, False otherwise
        return request.user and request.user.is_authenticated
