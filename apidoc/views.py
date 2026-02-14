from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from AutoReactGenerator.permissions import IsOwnerOrReadOnly, SubClassIsOwnerOrReadOnly
from project.models import Project

from .models import APIDoc, APIRequestBody, APIResponseBody
from .permissions import IsBodyOwner 
from .serializers import *

class APIRequestRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBodyOwner]
    queryset = APIRequestBody.objects.all()
    serializer_class = APIRequestBodySerializer

class APIRequestListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return APIRequestBodySerializer
        return APIRequestListSerializer
    
    def get_queryset(self):
        apidoc_id = self.kwargs.get('apidoc_id')
        return APIRequestBody.objects.filter(apidoc__id=apidoc_id)
    
    def perform_create(self, serializer):
        apidoc_id = self.kwargs.get('apidoc_id')
        apidoc = APIDoc.objects.get(id=apidoc_id)
        serializer.save(apidoc=apidoc)

class APIResponseRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBodyOwner]
    queryset = APIResponseBody.objects.all()
    serializer_class = APIResponseBodySerializer

class APIResponseListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return APIResponseBodySerializer
        return APIResponseListSerializer
    
    def get_queryset(self):
        apidoc_id = self.kwargs.get('apidoc_id')
        return APIResponseBody.objects.filter(apidoc__id=apidoc_id)
    
    def perform_create(self, serializer):
        apidoc_id = self.kwargs.get('apidoc_id')
        apidoc = APIDoc.objects.get(id=apidoc_id)
        serializer.save(apidoc=apidoc)

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
        serializer.save(created_by=self.request.user, project_under=project)

class APIDocRUDView(RetrieveUpdateDestroyAPIView):
    queryset = APIDoc.objects.select_related(
        'created_by', 
        'project_under'
        ).prefetch_related(
        'request_bodies', 
        'response_bodies'
    )    
    serializer_class = APIDocSerializer
    permission_classes = [IsOwnerOrReadOnly]
    