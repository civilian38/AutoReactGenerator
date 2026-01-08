from rest_framework.generics import ListCreateAPIView

from AutoReactGenerator.permissions import SubClassIsOwnerOrReadOnly

from .models import GenerationSession
from .serializers import *
from .paginations import *

class GenerationSessionLCView(ListCreateAPIView):
    permission_classes = [SubClassIsOwnerOrReadOnly, ]
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return GenerationSession.objects.filter(project_under__id=project_id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GenerationSessionCreateSerializer
        return GenerationSessionListSerializer
    
    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs.get('project_id'))
        serializer.save(project_under=project)

