from django.shortcuts import get_object_or_404
from django.db.models import F, Q
from django.db import transaction

from celery import chain

from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from AutoReactGenerator.permissions import SubClassIsOwnerOrReadOnly

from .models import GenerationSession
from .serializers import *
from .paginations import *
from .LLMService import get_folder_generation_prompt, get_generation_prompt, request_code_generation
from .tasks import request_file_generation_task, request_folder_generation_task
from .helper import _cleanup_empty_folders

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

        # fail test
        if session_object.project_under.to_do_request:
            return Response({"detail": "to do reqeust not accepted"}, status=status.HTTP_409_CONFLICT,)
        if session_object.is_occupied:
            return Response({"detail": "session occupied"}, status=status.HTTP_409_CONFLICT)
        elif session_object.status != "ACTIVE":
            return Response({"detail": "session not active"}, status=status.HTTP_409_CONFLICT)
        project_object = session_object.project_under

        with transaction.atomic():
            target_files = session_object.related_files.exclude(
                Q(draft_content__isnull=True) | Q(draft_content='')
            )

            updated_count = target_files.update(
                content=F('draft_content'),
                draft_content=None
            )

            session_object.related_pages.all().update(is_implemented=True)

            project_object.handover_context = project_object.handover_draft
            project_object.handover_draft = ""
            project_object.save()

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
        project_object = session_object.project_under

        # Fail Test
        if session_object.is_occupied:
            return Response({"detail": "session occupied"}, status=status.HTTP_409_CONFLICT)
        elif session_object.status != "ACTIVE":
            return Response({"detail": "session not active"}, status=status.HTTP_409_CONFLICT)

        with transaction.atomic():
            # delete newly created files and folders
            files_to_delete = session_object.related_files.filter(
                Q(content__isnull=True) | Q(content='')
            )
            candidate_folder_ids = set(files_to_delete.values_list('folder_id', flat=True))
            deleted_file_count, _ = files_to_delete.delete()
            deleted_folder_count = _cleanup_empty_folders(candidate_folder_ids)
            
            # discard update from existing files
            files_to_revert = session_object.related_files.exclude(
                Q(draft_content__isnull=True) | Q(draft_content='')
            )
            updated_file_count = files_to_revert.update(draft_content=None)

            # discard project handover (draft)
            project_object.handover_draft = ""
            project_object.save()

            # delete to do reqeust
            project_under = session_object.project_under
            project_under.to_do_request = None
            project_under.save()

            # update session status
            session_object.status = "DISCARDED"
            session_object.save()

        return Response(
            {
                "message": "Session discarded successfully.",
                "deleted_files_count": deleted_file_count,
                "deleted_folders_count": deleted_folder_count,
                "reverted_files_count": updated_file_count
            },
            status=status.HTTP_200_OK
        )

class SessionChatView(APIView):
    permission_classes = [IsAuthenticated, SubClassIsOwnerOrReadOnly]
    pagination_class = None

    def post(self, request, session_id):
        # 1. 세션 조회 및 권한 체크
        session_object = get_object_or_404(GenerationSession, pk=session_id)
        self.check_object_permissions(request, session_object)

        # 2. 상태 검증 (Fail Fast)
        if session_object.is_occupied:
            return Response({"detail": "session occupied"}, status=status.HTTP_409_CONFLICT)
        elif session_object.project_under.to_do_request:
            return Response({"detail": "to do request not accepted"}, status=status.HTTP_409_CONFLICT)
        elif session_object.status != "ACTIVE":
            return Response({"detail": "session not active"}, status=status.HTTP_409_CONFLICT)

        # 3. 데이터 검증
        serializer = SessionChatUserInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 4. 트랜잭션 시작
            with transaction.atomic():
                # 채팅 저장
                instance = serializer.save(session_under=session_object)

                # 세션 잠금
                session_object.is_occupied = True
                session_object.save()

                # 5. Celery Chain 구성 (폴더 생성 -> 파일 생성)
                workflow = chain(
                    request_folder_generation_task.si(session_id, request.user.id, instance.id),
                    request_file_generation_task.si(session_id, request.user.id, instance.id)
                )
                
                # 비동기 실행
                workflow.apply_async()
            
            # 트랜잭션이 성공적으로 커밋된 후에 응답 반환
            return Response({}, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response(
                {"error": f"Failed to start generation: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


"""
VIEWS FOR TEST
"""


class PromptTestView(APIView):
    permission_classes = [AllowAny,]
    pagination_class = None

    def get(self, request, session_id):
        return Response(
            {"data": get_generation_prompt(session_id)},
            status=status.HTTP_200_OK
        )

class FolderPromptTestView(APIView):
    permission_classes = [AllowAny,]
    pagination_class = None

    def get(self, request, session_id):
        return Response(
            {"data": get_folder_generation_prompt(session_id)},
            status=status.HTTP_200_OK
        )

class GenerationTestView(APIView):
    def get(self, request, session_id):
        try:
            user_id = request.user.id
            task = request_file_generation_task.delay(session_id, user_id, 0)
            return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response(
                {"error": str(e), "type": type(e).__name__}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FolderGenerationTestView(APIView):
    def get(self, request, session_id):
        try:
            user_id = request.user.id
            task = request_folder_generation_task.delay(session_id, user_id, 0)
            return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response(
                {"error": str(e), "type": type(e).__name__}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )