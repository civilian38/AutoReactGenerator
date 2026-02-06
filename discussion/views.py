from celery import chain
from django.db import transaction
from drf_yasg import openapi
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from AutoReactGenerator.permissions import IsOwnerOrReadOnly, SubClassIsOwnerOrReadOnly
from drf_yasg.utils import swagger_auto_schema, no_body

from .serializers import *
from .permissions import DiscussionChatIsOwnerOrReadOnly
from .tasks import get_chat_response_and_save, summarize_chat_and_save, make_short_summary_task

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
    permission_classes = [SubClassIsOwnerOrReadOnly]
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer

    def perform_update(self, serializer):
        serializer.save(project_under=serializer.instance.project_under)

class DiscussChatListView(ListAPIView):
    permission_classes = [DiscussionChatIsOwnerOrReadOnly]
    serializer_class = DiscussionChatSerializer
    pagination_class = None

    def get_queryset(self):
        discussion_id = self.kwargs.get('discussion_id')
        discussion = Discussion.objects.get(id=discussion_id)
        return DiscussionChat.objects.filter(discussion_under=discussion)


class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated, SubClassIsOwnerOrReadOnly]
    pagination_class = None

    @swagger_auto_schema(
        request_body=DiscussionChatSerializer,
        responses={
            202: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'task_id': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description='생성된 비동기 작업의 ID'
                    ),
                }
            ),
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def post(self, request, discussion_id):
        discussion_object = get_object_or_404(Discussion, id=discussion_id)
        self.check_object_permissions(request, discussion_object)

        if discussion_object.is_occupied:
            return Response(status=status.HTTP_409_CONFLICT)

        serializer = DiscussionChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save(discussion_under=discussion_object)
        discussion_object.is_occupied = True
        discussion_object.save()

        task = get_chat_response_and_save.delay(
            serializer.validated_data['content'],
            discussion_id,
            request.user.id,
            instance.id
        )
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

class ChatSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, SubClassIsOwnerOrReadOnly]
    pagination_class = None

    @swagger_auto_schema(
        request_body=no_body,
        responses={
            202: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'task_id': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description='생성된 비동기 작업의 ID'
                    ),
                }
            ),
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def post(self, request, discussion_id):
        try:
            discussion_object = Discussion.objects.get(id=discussion_id)
        except Discussion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, discussion_object)

        chats = DiscussionChat.objects.filter(discussion_under=discussion_object)
        if not chats.exists():
            return Response({"detail": "no chat exists"}, status=status.HTTP_400_BAD_REQUEST)

        workflow = chain(
            summarize_chat_and_save.si(discussion_id, request.user.id),
            make_short_summary_task.si(discussion_id, request.user.id)
        )
        workflow.apply_async()

        return Response({"detail": "async workflow initiated successfully"}, status=status.HTTP_202_ACCEPTED)
