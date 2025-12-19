from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from AutoReactGenerator.permissions import IsOwner
from .serializers import *
from frontFile.models import Folder

class ProjectLCAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectCreateSerializer

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

class ProjectRetrieveAPIView(RetrieveAPIView):
    serializer_class = ProjectRetrieveSerializer
    permission_classes = [IsOwner, ]
    queryset = Project.objects.all()