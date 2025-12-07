from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Project
from .serializers import ProjectLCSerializer
from frontFile.models import Folder

class ProjectLCAPIView(ListCreateAPIView):
    serializer_class = ProjectLCSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(created_by=user)

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        
        # root folder 생성
        Folder.objects.create(
            project_under=instance,
            parent_folder=None,
            name=instance.name
        )
