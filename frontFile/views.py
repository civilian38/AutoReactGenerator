from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema, no_body

from AutoReactGenerator.permissions import IsOwnerOrReadOnly, SubClassIsOwnerOrReadOnly
from project.models import Project

from .models import FrontFile
from .serializers import *

class FolderLCView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    @swagger_auto_schema(
            responses={
                200: FolderStructureSerializer,
                400: 'Bad Request',
                404: 'Not Found'
            }
    )
    def get(self, request, project_id, format=None):
        project = get_object_or_404(Project, id=project_id)
        root_folder = Folder.objects.filter(project_under=project, parent_folder__isnull=True).first()
        
        if not root_folder:
            return Response(
                {"detail": "no root folder exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FolderStructureSerializer(root_folder)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
            request_body=FolderCreateSerializer,
            responses={
                200: FolderRetrieveSerializer,
                400: 'Bad Request',
                404: 'Not Found'
            }
    )
    def post(self, request, project_id, format=None):
        project_object = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project_object)

        serializer = FolderCreateSerializer(data=request.data, context={'project': project_object})
        if serializer.is_valid(raise_exception=True):
            new_folder = serializer.save(project_under=project_object)
            response_serializer = FolderRetrieveSerializer(new_folder)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class FolderRUDView(RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    permission_classes = [SubClassIsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FolderRetrieveSerializer
        return FolderUpdateDeleteSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_object().project_under
        return context

    def perform_update(self, serializer):
        serializer.save(project_under=serializer.instance.project_under)


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
        project = Project.objects.get(self.kwargs.get('project_id'))
        serializer.save(created_by=self.request.user, project_under=project)

class FrontFileRUDView(RetrieveUpdateDestroyAPIView):
    queryset = FrontFile.objects.all()
    serializer_class = FrontFileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user, project_under=serializer.instance.project_under)