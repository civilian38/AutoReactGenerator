from django.urls import path
from .views import *

urlpatterns = [
    path('<int:project_id>/', FrontPageLCView.as_view(), name='frontpage-list-create'),
    path('detail/<int:pk>/', FrontPageRUDView.as_view(), name='frontpage-retrieve-update-delete')
]