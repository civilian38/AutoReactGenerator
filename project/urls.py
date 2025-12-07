from django.urls import path
from .views import ProjectLCAPIView, ProjectRetrieveAPIView

urlpatterns = [
    path('', ProjectLCAPIView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectRetrieveAPIView.as_view(), name='project-detail-create'),
]