from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ARUserRegisterView, GeminiAPIKeyView

urlpatterns = [
    # 회원가입 / 로그인 / 토큰 갱신
    path('register/', ARUserRegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API 키 조회(GET), 수정(Update)
    path('apikey/', GeminiAPIKeyView.as_view(), name='api_key_manage')
]