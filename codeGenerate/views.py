from django.shortcuts import get_object_or_404
from django.db.models import F, Q
from django.db import transaction

from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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

class SessionStatusCompletedView(APIView):
    def post(self, request, pk):
        session_object = get_object_or_404(GenerationSession, pk=pk)
        self.check_object_permissions(request, session_object)

        with transaction.atomic():
            target_files = session_object.related_files.exclude(
                Q(draft_content__isnull=True) | Q(draft_content='')
            )

            updated_count = target_files.update(
                content=F('draft_content'),
                draft_content=None  
            )

            session_object.status = "COMPLETED"
            session_object.save()

        return Response(
            {
                "message": "Session completed and files updated.", 
                "updated_files_count": updated_count
            }, 
            status=status.HTTP_200_OK
        )

class SessionStatusDiscardedView(APIView):
    def post(self, request, pk):
        session_object = get_object_or_404(GenerationSession, pk=pk)
        self.check_object_permissions(request, session_object)

        with transaction.atomic():
            target_files = session_object.related_files.exclude(
                Q(draft_content__isnull=True) | Q(draft_content='')
            )

            draft_count = target_files.update(
                draft_content=None  
            )

            session_object.status = "DISCARDED"
            session_object.save()

        return Response(
            {
                "message": "Session completed and draft contents discarded.", 
                "updated_files_count": draft_count
            }, 
            status=status.HTTP_200_OK
        )