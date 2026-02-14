from django.urls import path
from .views import *

urlpatterns = [
    path('<int:project_id>/', APIDocLCView.as_view(), name='apidoc-list-create'),
    path('detail/<int:pk>/', APIDocRUDView.as_view(), name='apidoc-retrieve-update-delete'),
    path('request/<int:pk>/', APIRequestRetrieveUpdateDestroyAPIView.as_view(), name='api-request-retrieve-update-delete'),
    path('requests/<int:apidoc_id>/', APIRequestListCreateAPIView.as_view(), name='api-request-list-create'),
    path('response/<int:pk>/', APIResponseRetrieveUpdateDestroyAPIView.as_view(), name='api-response-retrieve-update-delete'),
    path('responses/<int:apidoc_id>/', APIResponseListCreateAPIView.as_view(), name='api-response-list-create')
]