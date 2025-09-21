from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from AutoReactGenerator.permissions import IsOwnerOrReadOnly, SubPageIsOwnerOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from google import genai

from .models import *
from .serializers import *
from .LLMService import generate_response

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

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]
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

        serializer = DiscussionChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        response = generate_response(serializer.validated_data['content'], discussion_id, request.user.id)
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