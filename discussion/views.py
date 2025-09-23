from django.db import transaction
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from AutoReactGenerator.permissions import IsOwnerOrReadOnly, SubPageIsOwnerOrReadOnly
from drf_yasg.utils import swagger_auto_schema, no_body
from google import genai

from .models import *
from .serializers import *
from .LLMService import generate_response, summarize_chats
from .permissions import DiscussionChatIsOwnerOrReadOnly, IsProjectOwner

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

class DiscussChatListView(ListAPIView):
    permission_classes = [DiscussionChatIsOwnerOrReadOnly]
    serializer_class = DiscussionChatSerializer

    def get_queryset(self):
        discussion_id = self.kwargs.get('discussion_id')
        discussion = Discussion.objects.get(id=discussion_id)
        return DiscussionChat.objects.filter(discussion_under=discussion)


class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwner]
    pagination_class = None

    @swagger_auto_schema(
        request_body=DiscussionChatSerializer,
        responses={
            200: DiscussionChatLLMSerializer,
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def post(self, request, discussion_id, format=None):
        try:
            discussion_object = Discussion.objects.get(id=discussion_id)
        except Discussion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, discussion_object)

        serializer = DiscussionChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        response = generate_response(serializer.validated_data['content'], discussion_id, request.user.id)

        if not isinstance(response, str):
            return response

        serializer.save(discussion_under=discussion_object)

        llm_response_data = {
            'discussion_under': discussion_id,
            'content': response,
             'is_by_user': False
        }
        llm_response_serializer = DiscussionChatLLMSerializer(data=llm_response_data)
        if not llm_response_serializer.is_valid():
            return Response(llm_response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        llm_response_serializer.save()
        return Response(llm_response_serializer.data)

class ChatSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwner]
    pagination_class = None


    @swagger_auto_schema(
        request_body=no_body,
        responses={
            200: DiscussionSerializer,
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def post(self, request, discussion_id, format=None):
        try:
            discussion_object = Discussion.objects.get(id=discussion_id)
        except Discussion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, discussion_object)

        chats = DiscussionChat.objects.filter(discussion_under=discussion_object)
        if not chats.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                summary_content = summarize_chats(discussion_id, request.user.id)
                if not isinstance(summary_content, str):
                    return summary_content

                update_data = {'summary': summary_content}
                serializer = DiscussionSummarySerializer(instance=discussion_object, data=update_data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                chats.delete()
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
            {
                    "type": "UnexpectedError",
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
