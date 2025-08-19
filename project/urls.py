from django.urls import path
from .views import ProjectLCAPIView


urlpatterns = [
    path('', ProjectLCAPIView.as_view(), name='project-list-create')
]