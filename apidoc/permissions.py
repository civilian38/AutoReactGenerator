from rest_framework import permissions

class IsBodyOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
           return True
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            return obj.apidoc.project_under.created_by == request.user
        return False
    