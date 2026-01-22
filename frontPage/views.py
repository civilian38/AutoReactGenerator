from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from AutoReactGenerator.permissions import IsOwnerOrReadOnly, SubClassIsOwnerOrReadOnly
from project.models import Project
from .models import FrontPage
from .serializers import *

class FrontPageLCView(ListCreateAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return FrontPage.objects.filter(project_under__id=project_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FrontPageSerializer
        return FrontPageListSerializer

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs.get('project_id'))
        serializer.save(project_under=project, is_implemented=False)

class FrontPageRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes = [SubClassIsOwnerOrReadOnly]
    queryset = FrontPage.objects.all()
    serializer_class = FrontPageSerializer

    def perform_update(self, serializer):
        serializer.save(project_under=serializer.instance.project_under, is_implemented=False)
