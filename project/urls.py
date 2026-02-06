from django.urls import path
from .views import ProjectLCAPIView, ProjectRetrieveUpdateDestroyAPIView, ProjectToDoRequestAcceptAPIView

urlpatterns = [
    path('', ProjectLCAPIView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectRetrieveUpdateDestroyAPIView.as_view(), name='project-rud'),
    # path('<int:project_id>/todoaccept/', ProjectToDoRequestAcceptAPIView.as_view(), name='project-todo-accept'),
]