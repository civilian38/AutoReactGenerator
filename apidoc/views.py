from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from AutoReactGenerator.permissions import IsOwnerOrReadOnly
from project.models import Project

from .models import APIDoc
from .serializers import *

class APIDocLCView(ListCreateAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return APIDocCreateSerializer
        return APIDocListSerializer
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return APIDoc.objects.filter(project_under__id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        project = Project.objects.get(id=project_id)
        serializer.save(project_under=project)

class APIDocRUDView(RetrieveUpdateDestroyAPIView):
    queryset = APIDoc.objects.all()
    serializer_class = APIDocSerializer
    permission_classes = [IsOwnerOrReadOnly]