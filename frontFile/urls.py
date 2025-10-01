from django.urls import path
from .views import *

urlpatterns = [
    path('<int:project_id>/folders/', FolderLCView.as_view(), name='folder-list-create'),
    path('folders/<int:pk>/', FolderRUDView.as_view(), name='folder-retrieve-update-delete')
]