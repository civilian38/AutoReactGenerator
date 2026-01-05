from django.urls import path
from .views import *

urlpatterns = [
    path('<int:project_id>/folders/', FolderLCView.as_view(), name='folder-list-create'),
    path('folder/<int:pk>/', FolderRUDView.as_view(), name='folder-retrieve-update-delete'),
    path('projectfile/create/', ProjectFileCView.as_view(), name='file-create-view'),
    path('projectfile/<int:pk>/', ProjectFileRUDView.as_view(), name='file-retrieve-update-delete'),
    path('projectfile/<int:pk>/draft', ProjectFileApplyDraftView.as_view(), name='file-apply-draft')
]