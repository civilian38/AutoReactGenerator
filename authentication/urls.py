from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ARUserRegisterView # 위에서 만든 회원가입 뷰

urlpatterns = [
    # 회원가입
    path('register/', ARUserRegisterView.as_view(), name='register'),

    # 로그인 (JWT 토큰 발급)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # 토큰 갱신
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]