from django.shortcuts import get_object_or_404
from django.db.models import F, Q
from django.db import transaction

from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from AutoReactGenerator.permissions import SubClassIsOwnerOrReadOnly

from .models import GenerationSession
from .serializers import *
from .paginations import *
from .LLMService import get_generation_prompt, request_code_generation
from .tasks import request_generate_and_apply

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

class SessionChatView(APIView):
    permission_classes = [IsAuthenticated, SubClassIsOwnerOrReadOnly]
    pagination_class = None
    def post(self, request, session_id):
        session_object = get_object_or_404(GenerationSession, pk=session_id)
        self.check_object_permissions(request, session_object)

        if session_object.is_occupied:
            return Response({"detail": "session occupied"}, status=status.HTTP_409_CONFLICT,)
        elif session_object.status != "ACTIVE":
            return Response({"detail": "session not active"}, status=status.HTTP_409_CONFLICT)

        serializer = SessionChatUserInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save(session_under=session_object)

        session_object.is_occupied = True
        session_object.save()

        task = request_generate_and_apply.delay(
            session_id,
            request.user.id,
            instance.id
        )
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

class PromptTestView(APIView):
    permission_classes = [AllowAny,]
    pagination_class = None

    def get(self, request, session_id):
        session_object = get_object_or_404(GenerationSession, pk=session_id)
        self.check_object_permissions(request, session_object)

        return Response(
            {"data": get_generation_prompt(session_id)},
            status=status.HTTP_200_OK
        )

class GenerationTestView(APIView):
    def get(self, request, session_id):
        try:
            user_id = request.user.id
            generation_result = request_code_generation(session_id, user_id)

            response_data = generation_result.model_dump(mode='json')

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e), "type": type(e).__name__}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
