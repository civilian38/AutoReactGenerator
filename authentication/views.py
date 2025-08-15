from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ARUserRegisterSerializer
from .models import ARUser

class ARUserRegisterView(CreateAPIView):
    queryset = ARUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = ARUserRegisterSerializer