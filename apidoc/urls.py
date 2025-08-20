from django.urls import path
from .views import *

urlpatterns = [
    path('<int:project_id>/', APIDocLCView.as_view(), name='apidoc-list-create'),
    path('detail/<int:pk>/', APIDocRUDView.as_view(), name='apidoc-retrieve-update-delete')
]