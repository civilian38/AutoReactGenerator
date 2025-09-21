from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from AutoReactGenerator.permissions import IsOwnerOrReadOnly, SubPageIsOwnerOrReadOnly

from .models import *
from .serializers import *


class DiscussionLCView(ListCreateAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Discussion.objects.filter(project_under__id=project_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DiscussionSerializer
        return DiscussionListSerializer

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs.get('project_id'))
        serializer.save(project_under=project)

class DiscussionRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes = [SubPageIsOwnerOrReadOnly]
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer

    def perform_update(self, serializer):
        serializer.save(project_under=serializer.instance.project_under)