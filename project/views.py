from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from AutoReactGenerator.permissions import IsOwner
from frontFile.models import Folder
from .serializers import *

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

class ProjectToDoRequestAcceptAPIView(APIView):
    permission_classes = [IsOwner, ]
    
    def post(self, request, project_id):
        project_object = get_object_or_404(Project, pk=project_id)
        self.check_object_permissions(request, project_object)

        if project_object.to_do_request == "":
            return Response(
                {"message": "Request Already Accepted"},
                status=status.HTTP_200_OK
            )
        
        project_object.to_do_request = ""
        project_object.save()

        return Response(
            {
                "message": "Project To Do Request Accepted"
            }, 
        )

"""
Only For test
"""

class ProjectTestRetrieveAPIView(RetrieveAPIView):
    serializer_class = TestProjectSerializer
    permission_classes = [IsOwner, ]
    queryset = Project.objects.all()