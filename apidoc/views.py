from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db import transaction

from AutoReactGenerator.permissions import IsOwnerOrReadOnly, SubClassIsOwnerOrReadOnly
from project.models import Project

from .models import APIDoc, APIRequestBody, APIResponseBody
from .permissions import IsBodyOwner, IsParameterOwner
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

class URLParameterListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsParameterOwner]
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return URLParameterCreateSerializer
        return URLParameterListSerializer
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return URLParameter.objects.filter(project_under__id=project_id).prefetch_related('apidocs')

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        project = Project.objects.get(id=project_id)
        serializer.save(project_under=project)

class URLParameterRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsParameterOwner]
    serializer_class = URLParameterRetrieveUpdateSerializer
    queryset = URLParameter.objects.prefetch_related('apidocs').all()

class ParameterRelationUpdateView(APIView):
    def post(self, request, apidoc_id):
        apidoc = get_object_or_404(APIDoc, id=apidoc_id)
        self.check_object_permissions(request, apidoc)
        
        serializer = ParameterRelationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        to_add_ids = serializer.validated_data['to_add']
        to_pop_ids = serializer.validated_data['to_pop']
        project = apidoc.project_under

        try:
            with transaction.atomic():
                
                if to_add_ids:
                    params_to_add = URLParameter.objects.filter(
                        id__in=to_add_ids, 
                        project_under=project
                    )
                    if params_to_add.exists():
                        apidoc.url_parameters.add(*params_to_add)

                if to_pop_ids:
                    params_to_remove = URLParameter.objects.filter(id__in=to_pop_ids)
                    if params_to_remove.exists():
                        apidoc.url_parameters.remove(*params_to_remove)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = APIDocSerializer(apidoc, context={'request': request}).data
        
        return Response(data, status=status.HTTP_200_OK)