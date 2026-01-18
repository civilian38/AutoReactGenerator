from django.urls import path
from .views import ProjectLCAPIView, ProjectRetrieveAPIView, ProjectToDoRequestAcceptAPIView

urlpatterns = [
    path('', ProjectLCAPIView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectRetrieveAPIView.as_view(), name='project-detail-create'),
    path('<int:project_id>/todoaccept/', ProjectToDoRequestAcceptAPIView.as_view(), name='project-todo-accept'),
]