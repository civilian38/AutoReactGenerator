from rest_framework import permissions

class DiscussionChatIsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.discussion_under.project_under.created_by == request.user