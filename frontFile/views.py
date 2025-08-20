from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from AutoReactGenerator.permissions import IsOwnerOrReadOnly
from project.models import Project

from .models import FrontFile
from .serializers import *

class FrontFileLCView(ListCreateAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FrontFileCreateSerializer
        return FrontFileListSerializer
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return FrontFile.objects.filter(project_under__id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        project = Project.objects.get(id=project_id)
        serializer.save(created_by=self.request.user, project_under=project)

class FrontFileRUDView(RetrieveUpdateDestroyAPIView):
    queryset = FrontFile.objects.all()
    serializer_class = FrontFileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)