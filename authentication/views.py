from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import ARUserRegisterSerializer, GeminiKeySerializer
from .models import ARUser

class ARUserRegisterView(CreateAPIView):
    queryset = ARUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = ARUserRegisterSerializer

class GeminiAPIKeyView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeminiKeySerializer

    def get_object(self):
        return self.request.user