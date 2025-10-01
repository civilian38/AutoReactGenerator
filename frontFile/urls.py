from django.urls import path
from .views import *

urlpatterns = [
    path('<int:project_id>/folders/', FolderLCView.as_view(), name='folder-list-create'),
    path('<int:project_id>/', FrontFileLCView.as_view(), name='frontfile-list-create'),
    path('detail/<int:pk>/', FrontFileRUDView.as_view(), name='frontfile-retrieve-update-delete')
]